#!/usr/bin/env python3
from datetime import datetime
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
import csv
import json
import mimetypes
import os
import re


BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
WARDROBE_DIR = Path(os.environ.get("WARDROBE_DIR", BASE_DIR.parent / "Roupinhas")).resolve()
PORT = int(os.environ.get("PORT", "8080"))

IMAGE_EXTENSIONS = {
    ".avif",
    ".gif",
    ".heic",
    ".heif",
    ".jpeg",
    ".jpg",
    ".png",
    ".webp",
}


def is_image(path):
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def image_files(folder_path):
    if not folder_path.exists():
        return []
    return sorted(
        (path for path in folder_path.iterdir() if is_image(path)),
        key=lambda item: item.name.lower(),
    )


def folder_url(folder, filename):
    return f"/media/{quote(folder, safe='')}/{quote(filename, safe='')}"


def current_stamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")


def clean_filename_parts(filename, fallback="foto"):
    raw_name = str(filename or fallback).replace("\\", "/")
    raw_name = Path(raw_name).name
    suffix = Path(raw_name).suffix.lower()
    stem = Path(raw_name).stem or fallback
    stem = re.sub(r"[\x00-\x1f\x7f]+", " ", stem)
    stem = re.sub(r'[/:*?"<>|\\]+', "_", stem)
    stem = re.sub(r"\s+", "_", stem).strip(" ._")
    return stem or fallback, suffix


def folder_from_segment(segment):
    folder = unquote(segment)
    if not folder or folder in {".", ".."} or "/" in folder or "\\" in folder:
        return None

    path = (WARDROBE_DIR / folder).resolve()
    if path != WARDROBE_DIR and WARDROBE_DIR in path.parents and path.is_dir():
        return folder, path
    return None


def file_from_segments(folder_segment, file_segment):
    resolved_folder = folder_from_segment(folder_segment)
    if not resolved_folder:
        return None

    folder, folder_path = resolved_folder
    filename = Path(unquote(file_segment)).name
    file_path = (folder_path / filename).resolve()
    if folder_path in file_path.parents and is_image(file_path):
        return folder, filename, file_path
    return None


def safe_upload_name(filename):
    stem, suffix = clean_filename_parts(filename)
    if suffix not in IMAGE_EXTENSIONS:
        suffix = ".jpeg"

    return f"{current_stamp()}_{stem}{suffix}"


def safe_rename_name(filename, current_suffix):
    stem, requested_suffix = clean_filename_parts(filename)
    suffix = requested_suffix if requested_suffix in IMAGE_EXTENSIONS else current_suffix
    return f"{stem}{suffix.lower()}"


def image_payload(folder, file_path):
    return {
        "name": file_path.name,
        "label": file_path.stem.replace("_", " "),
        "url": folder_url(folder, file_path.name),
        "modified": int(file_path.stat().st_mtime),
    }


def read_csv_rows(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file, delimiter=";"))


def report_payload():
    detail_rows = read_csv_rows(WARDROBE_DIR / "classificacao_roupinhas_isabel.csv")
    summary_rows = read_csv_rows(WARDROBE_DIR / "resumo_classificacao_roupinhas_isabel.csv")
    image_count = sum(1 for path in WARDROBE_DIR.rglob("*") if is_image(path))
    folders = sorted({row.get("tamanho_pasta", "") for row in detail_rows if row.get("tamanho_pasta")})
    groups = sorted({row.get("grupo", "") for row in detail_rows if row.get("grupo")})

    by_size = {}
    by_group = {}
    for row in detail_rows:
        quantity = int(row.get("quantidade") or "1")
        by_size[row.get("tamanho_pasta", "Sem Pasta")] = by_size.get(row.get("tamanho_pasta", "Sem Pasta"), 0) + quantity
        by_group[row.get("grupo", "Sem Grupo")] = by_group.get(row.get("grupo", "Sem Grupo"), 0) + quantity

    return {
        "totals": {
            "images": image_count,
            "classified": len(detail_rows),
            "folders": len(folders),
            "groups": len(groups),
        },
        "bySize": [{"name": key, "quantity": by_size[key]} for key in sorted(by_size)],
        "byGroup": [{"name": key, "quantity": by_group[key]} for key in sorted(by_group)],
        "summary": summary_rows,
        "details": detail_rows,
    }


def unique_path(folder_path, filename):
    target = folder_path / filename
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    counter = 2
    while True:
        candidate = folder_path / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


class ArmarioHandler(BaseHTTPRequestHandler):
    server_version = "ArmarioIsabel/1.0"

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, cache=True):
        if not path.exists() or not path.is_file():
            self.send_error(404)
            return

        content_type, _ = mimetypes.guess_type(path.name)
        if path.suffix.lower() == ".webmanifest":
            content_type = "application/manifest+json"
        if path.suffix.lower() == ".heic":
            content_type = "image/heic"
        if path.suffix.lower() == ".heif":
            content_type = "image/heif"

        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        if cache:
            self.send_header("Cache-Control", "public, max-age=3600")
        else:
            self.send_header("Cache-Control", "no-store")
        if path.name == "sw.js":
            self.send_header("Service-Worker-Allowed", "/")
        self.end_headers()
        self.wfile.write(body)

    def static_path(self, request_path):
        clean_path = "index.html" if request_path == "/" else request_path.lstrip("/")
        candidate = (PUBLIC_DIR / clean_path).resolve()
        if candidate == PUBLIC_DIR or PUBLIC_DIR not in candidate.parents:
            return None
        return candidate

    def do_GET(self):
        parsed = urlparse(self.path)
        request_path = parsed.path

        if request_path == "/api/folders":
            folders = []
            if WARDROBE_DIR.exists():
                for folder_path in sorted(
                    (path for path in WARDROBE_DIR.iterdir() if path.is_dir()),
                    key=lambda item: item.name.lower(),
                ):
                    files = image_files(folder_path)
                    preview = folder_url(folder_path.name, files[0].name) if files else None
                    folders.append(
                        {
                            "name": folder_path.name,
                            "count": len(files),
                            "preview": preview,
                        }
                    )
            self.send_json({"folders": folders})
            return

        if request_path == "/api/report":
            self.send_json(report_payload())
            return

        if request_path.startswith("/api/folders/"):
            folder_segment = request_path.removeprefix("/api/folders/")
            resolved = folder_from_segment(folder_segment)
            if not resolved:
                self.send_json({"error": "Pasta nao encontrada."}, status=404)
                return

            folder, folder_path = resolved
            images = [image_payload(folder, file_path) for file_path in image_files(folder_path)]
            self.send_json({"folder": folder, "images": images})
            return

        if request_path.startswith("/media/"):
            rest = request_path.removeprefix("/media/")
            if "/" not in rest:
                self.send_error(404)
                return
            folder_segment, file_segment = rest.split("/", 1)
            resolved = file_from_segments(folder_segment, file_segment)
            if not resolved:
                self.send_error(404)
                return

            _, _, file_path = resolved
            self.send_file(file_path)
            return

        path = self.static_path(request_path)
        if path:
            self.send_file(path, cache=False)
            return
        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        request_path = parsed.path

        if not request_path.startswith("/api/folders/"):
            self.send_json({"error": "Rota nao encontrada."}, status=404)
            return

        if request_path.endswith("/rename"):
            self.rename_image(request_path)
            return

        if not request_path.endswith("/upload"):
            self.send_json({"error": "Rota nao encontrada."}, status=404)
            return

        self.upload_image(request_path)

    def upload_image(self, request_path):
        folder_segment = request_path.removeprefix("/api/folders/").removesuffix("/upload")
        folder_segment = folder_segment.rstrip("/")
        resolved = folder_from_segment(folder_segment)
        if not resolved:
            self.send_json({"error": "Pasta nao encontrada."}, status=404)
            return

        folder, folder_path = resolved
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self.send_json({"error": "Envie uma imagem pelo formulario."}, status=400)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0

        if length <= 0:
            self.send_json({"error": "Arquivo vazio."}, status=400)
            return

        body = self.rfile.read(length)
        message = BytesParser(policy=default).parsebytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
            + body
        )

        uploaded = None
        for part in message.iter_parts():
            field_name = part.get_param("name", header="content-disposition")
            if field_name not in {"image", "file", "photo"}:
                continue
            uploaded = part
            break

        if not uploaded:
            self.send_json({"error": "Imagem nao encontrada no envio."}, status=400)
            return

        filename = safe_upload_name(uploaded.get_filename())
        data = uploaded.get_payload(decode=True)
        if not data:
            self.send_json({"error": "Arquivo vazio."}, status=400)
            return

        target = unique_path(folder_path, filename)
        target.write_bytes(data)

        self.send_json(
            {
                "folder": folder,
                "image": image_payload(folder, target),
            },
            status=201,
        )

    def rename_image(self, request_path):
        folder_segment = request_path.removeprefix("/api/folders/").removesuffix("/rename")
        folder_segment = folder_segment.rstrip("/")
        resolved = folder_from_segment(folder_segment)
        if not resolved:
            self.send_json({"error": "Pasta nao encontrada."}, status=404)
            return

        folder, folder_path = resolved
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            self.send_json({"error": "Envie o novo nome em JSON."}, status=400)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = self.rfile.read(length).decode("utf-8")
            payload = json.loads(data or "{}")
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            self.send_json({"error": "Nao consegui ler o novo nome."}, status=400)
            return

        old_name = Path(str(payload.get("oldName") or payload.get("name") or "")).name
        new_name = str(payload.get("newName") or "").strip()
        if not old_name or not new_name:
            self.send_json({"error": "Informe a foto e o novo nome."}, status=400)
            return

        current_path = (folder_path / old_name).resolve()
        if folder_path not in current_path.parents or not is_image(current_path):
            self.send_json({"error": "Foto nao encontrada."}, status=404)
            return

        target_name = safe_rename_name(new_name, current_path.suffix)
        target_path = (folder_path / target_name).resolve()
        if target_path != current_path:
            target_path = unique_path(folder_path, target_name)
            current_path.rename(target_path)

        self.send_json({"folder": folder, "image": image_payload(folder, target_path)})


def main():
    WARDROBE_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), ArmarioHandler)
    print(f"O Armario da Isabel aberto em http://0.0.0.0:{PORT}")
    print(f"Lendo as roupinhas de: {WARDROBE_DIR}")
    server.serve_forever()


if __name__ == "__main__":
    main()
