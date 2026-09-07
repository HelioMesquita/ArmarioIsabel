#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import csv
import hashlib
import json
import os
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
PUBLIC_DIR = BASE_DIR / "public"
WARDROBE_DIR = Path(os.environ.get("WARDROBE_DIR", BASE_DIR / "Roupinhas")).resolve()

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


def read_csv_rows(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file, delimiter=";"))


def image_url(folder, filename, media_prefix):
    return f"{media_prefix}/{quote(folder, safe='')}/{quote(filename, safe='')}"


def image_payload(folder, file_path, media_prefix):
    return {
        "name": file_path.name,
        "label": file_path.stem.replace("_", " "),
        "url": image_url(folder, file_path.name, media_prefix),
        "modified": int(file_path.stat().st_mtime),
    }


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
        size = row.get("tamanho_pasta", "Sem Pasta")
        group = row.get("grupo", "Sem Grupo")
        by_size[size] = by_size.get(size, 0) + quantity
        by_group[group] = by_group.get(group, 0) + quantity

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


def build_catalog(media_prefix):
    folders = []
    image_paths = []

    if WARDROBE_DIR.exists():
        for folder_path in sorted(
            (path for path in WARDROBE_DIR.iterdir() if path.is_dir()),
            key=lambda item: item.name.lower(),
        ):
            files = image_files(folder_path)
            images = []

            for file_path in files:
                image = image_payload(folder_path.name, file_path, media_prefix)
                images.append(image)
                image_paths.append(f"./{image['url']}")

            folders.append(
                {
                    "name": folder_path.name,
                    "count": len(images),
                    "preview": images[0]["url"] if images else None,
                    "images": images,
                }
            )

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "folders": folders,
        "report": report_payload(),
    }, image_paths


def write_json(path, payload):
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_static_config(target_dir, generated_at):
    write_json(
        target_dir / "app-config.json",
        {
            "mode": "static",
            "dataSource": "catalog",
            "readOnly": True,
            "apiBaseUrl": "",
            "catalogUrl": "catalog.json",
            "generatedAt": generated_at,
        },
    )


def write_static_service_worker(target_dir, build_id, copied_images, app_assets=None):
    public_sw = (PUBLIC_DIR / "sw.js").read_text(encoding="utf-8")
    extra_precache = ["./catalog.json"]
    if "--precache-images" in sys.argv:
        extra_precache.extend(copied_images)

    preamble = (
        f"self.ARMARIO_CACHE_NAME = {json.dumps(f'armario-isabel-static-{build_id}')};\n"
        f"self.ARMARIO_APP_ASSETS = {json.dumps(app_assets, ensure_ascii=False, indent=2) if app_assets else 'undefined'};\n"
        f"self.ARMARIO_EXTRA_PRECACHE = {json.dumps(extra_precache, ensure_ascii=False, indent=2)};\n"
    )
    (target_dir / "sw.js").write_text(preamble + public_sw, encoding="utf-8")


def write_root_index():
    index = (PUBLIC_DIR / "index.html").read_text(encoding="utf-8")
    replacements = {
        'href="icons/icon.svg"': 'href="public/icons/icon.svg"',
        'href="icons/icon-180.png"': 'href="public/icons/icon-180.png"',
        'href="styles.css"': 'href="public/styles.css"',
        'src="app.js"': 'src="public/app.js"',
    }
    for old, new in replacements.items():
        index = index.replace(old, new)
    (BASE_DIR / "index.html").write_text(index, encoding="utf-8")


def write_root_manifest():
    manifest = json.loads((PUBLIC_DIR / "manifest.webmanifest").read_text(encoding="utf-8"))
    manifest["start_url"] = "./"
    manifest["scope"] = "./"
    for icon in manifest.get("icons", []):
        icon["src"] = f"public/{icon['src'].lstrip('./')}"
    write_json(BASE_DIR / "manifest.webmanifest", manifest)


def write_root_pages_files():
    catalog, image_paths = build_catalog("Roupinhas")
    catalog_json = json.dumps(catalog, ensure_ascii=False, sort_keys=True)
    build_id = hashlib.sha256(catalog_json.encode("utf-8")).hexdigest()[:12]
    app_assets = [
        "./",
        "./index.html",
        "./public/app.js",
        "./public/styles.css",
        "./app-config.json",
        "./manifest.webmanifest",
        "./public/icons/icon.svg",
        "./public/icons/icon-180.png",
        "./public/icons/icon-192.png",
        "./public/icons/icon-512.png",
    ]

    write_root_index()
    write_root_manifest()
    write_json(BASE_DIR / "catalog.json", catalog)
    write_static_config(BASE_DIR, catalog["generatedAt"])
    write_static_service_worker(BASE_DIR, build_id, image_paths, app_assets=app_assets)
    (BASE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    return catalog, image_paths


def main():
    if not PUBLIC_DIR.exists():
        raise RuntimeError("Diretorio public nao encontrado.")

    root_catalog, root_images = write_root_pages_files()

    print(
        "Arquivos de GitHub Pages gerados na raiz "
        f"com {len(root_catalog['folders'])} pastas e {len(root_images)} imagens."
    )


if __name__ == "__main__":
    main()
