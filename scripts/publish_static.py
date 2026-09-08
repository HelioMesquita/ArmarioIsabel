#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import csv
import hashlib
import json
import os
import shutil
import struct
import sys
import zlib


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_PUBLIC_DIR = BASE_DIR / "project" / "public"
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

WEB_ICON_SIZES = (180, 192, 512)


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


def color(hex_color, alpha=255):
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
        alpha,
    )


def in_rounded_rect(x, y, left, top, right, bottom, radius):
    if left + radius <= x < right - radius or top + radius <= y < bottom - radius:
        return left <= x < right and top <= y < bottom

    corner_x = left + radius if x < left + radius else right - radius - 1
    corner_y = top + radius if y < top + radius else bottom - radius - 1
    return (x - corner_x) ** 2 + (y - corner_y) ** 2 <= radius**2


def paint_pixel(pixels, size, x, y, rgba):
    if 0 <= x < size and 0 <= y < size:
        offset = (y * size + x) * 4
        pixels[offset : offset + 4] = bytes(rgba)


def draw_rect(pixels, size, left, top, right, bottom, rgba):
    for y in range(max(0, top), min(size, bottom)):
        for x in range(max(0, left), min(size, right)):
            paint_pixel(pixels, size, x, y, rgba)


def draw_rounded_rect(pixels, size, left, top, right, bottom, radius, rgba):
    for y in range(max(0, top), min(size, bottom)):
        for x in range(max(0, left), min(size, right)):
            if in_rounded_rect(x, y, left, top, right, bottom, radius):
                paint_pixel(pixels, size, x, y, rgba)


def draw_circle(pixels, size, center_x, center_y, radius, rgba):
    radius_squared = radius**2
    for y in range(max(0, center_y - radius), min(size, center_y + radius + 1)):
        for x in range(max(0, center_x - radius), min(size, center_x + radius + 1)):
            if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius_squared:
                paint_pixel(pixels, size, x, y, rgba)


def draw_globe_mark(pixels, size, center_x, center_y, radius):
    blue = color("#2f7de1")
    white = color("#ffffff")
    draw_circle(pixels, size, center_x, center_y, radius, blue)

    stroke = max(2, size // 64)
    radius_squared = radius**2
    inner_radius = radius - stroke
    inner_squared = inner_radius**2

    for y in range(center_y - radius, center_y + radius + 1):
        for x in range(center_x - radius, center_x + radius + 1):
            distance = (x - center_x) ** 2 + (y - center_y) ** 2
            inside = distance <= radius_squared
            if not inside:
                continue

            on_outer_ring = distance >= inner_squared
            on_vertical = abs(x - center_x) <= stroke
            on_horizontal = abs(y - center_y) <= stroke
            on_top_parallel = abs(y - (center_y - radius // 3)) <= stroke
            on_bottom_parallel = abs(y - (center_y + radius // 3)) <= stroke

            if on_outer_ring or on_vertical or on_horizontal or on_top_parallel or on_bottom_parallel:
                paint_pixel(pixels, size, x, y, white)


def png_chunk(name, payload):
    chunk = name + payload
    return (
        struct.pack(">I", len(payload))
        + chunk
        + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)
    )


def write_png(path, size, pixels):
    rows = []
    stride = size * 4
    for y in range(size):
        rows.append(b"\x00" + bytes(pixels[y * stride : (y + 1) * stride]))

    payload = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)),
            png_chunk(b"IDAT", zlib.compress(b"".join(rows), 9)),
            png_chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(payload)


def write_web_png_icon(path, size):
    pixels = bytearray([0, 0, 0, 0] * size * size)
    scale = size / 512
    px = lambda value: int(round(value * scale))

    draw_rounded_rect(pixels, size, 0, 0, size, size, px(96), color("#edf8ff"))
    draw_rounded_rect(pixels, size, px(78), px(104), px(434), px(434), px(28), color("#cfeaff"))
    draw_rect(pixels, size, px(104), px(132), px(408), px(408), color("#ffffff"))
    draw_rect(pixels, size, px(128), px(166), px(384), px(194), color("#2f7de1"))
    draw_rect(pixels, size, px(172), px(204), px(264), px(368), color("#f48aae"))
    draw_rect(pixels, size, px(260), px(204), px(352), px(368), color("#a7d8f3"))
    draw_rect(pixels, size, px(104), px(408), px(408), px(442), color("#58b7a8"))
    draw_circle(pixels, size, px(218), px(292), px(10), color("#ffffff"))
    draw_circle(pixels, size, px(306), px(292), px(10), color("#ffffff"))
    draw_globe_mark(pixels, size, px(372), px(140), px(70))
    write_png(path, size, pixels)


def write_web_svg_icon(path):
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="96" fill="#edf8ff"/>
  <path d="M78 104h356v330H78z" fill="#cfeaff"/>
  <path d="M104 132h304v276H104z" fill="#fff"/>
  <path d="M128 166h256v28H128z" fill="#2f7de1"/>
  <path d="M172 204h92v164h-92z" fill="#f48aae"/>
  <path d="M260 204h92v164h-92z" fill="#a7d8f3"/>
  <path d="M104 408h304v34H104z" fill="#58b7a8"/>
  <circle cx="218" cy="292" r="10" fill="#fff"/>
  <circle cx="306" cy="292" r="10" fill="#fff"/>
  <circle cx="372" cy="140" r="70" fill="#2f7de1"/>
  <circle cx="372" cy="140" r="50" fill="none" stroke="#fff" stroke-width="12"/>
  <path d="M302 140h140M372 70v140M322 118h100M322 162h100" stroke="#fff" stroke-width="12" stroke-linecap="round"/>
</svg>
""",
        encoding="utf-8",
    )


def write_web_icons(icons_target):
    icons_target.mkdir(parents=True, exist_ok=True)
    write_web_svg_icon(icons_target / "web-icon.svg")
    for size in WEB_ICON_SIZES:
        write_web_png_icon(icons_target / f"web-icon-{size}.png", size)


def static_runtime_config(generated_at):
    return {
        "mode": "static",
        "dataSource": "catalog",
        "readOnly": True,
        "apiBaseUrl": "",
        "catalogUrl": "catalog.json",
        "generatedAt": generated_at,
        "features": {
            "upload": False,
            "rename": False,
        },
    }


def write_static_config(target_dir, config):
    write_json(target_dir / "app-config.json", config)


def static_config_script(config):
    payload = json.dumps(config, ensure_ascii=False, indent=2).replace("</", "<\\/")
    lines = payload.splitlines()
    config_lines = [f"      window.ARMARIO_APP_CONFIG = {lines[0]}"]
    config_lines.extend(f"      {line}" for line in lines[1:])

    return (
        "    <script>\n"
        + "\n".join(config_lines)
        + ";\n"
        '      document.documentElement.dataset.armarioMode = "static";\n'
        "    </script>\n"
    )


def write_static_service_worker(target_dir, build_id, copied_images, app_assets=None):
    public_sw = (PROJECT_PUBLIC_DIR / "sw.js").read_text(encoding="utf-8")
    extra_precache = ["./catalog.json"]
    if "--precache-images" in sys.argv:
        extra_precache.extend(copied_images)

    preamble = (
        f"self.ARMARIO_CACHE_NAME = {json.dumps(f'armario-isabel-static-{build_id}')};\n"
        f"self.ARMARIO_APP_ASSETS = {json.dumps(app_assets, ensure_ascii=False, indent=2) if app_assets else 'undefined'};\n"
        f"self.ARMARIO_EXTRA_PRECACHE = {json.dumps(extra_precache, ensure_ascii=False, indent=2)};\n"
    )
    (target_dir / "sw.js").write_text(preamble + public_sw, encoding="utf-8")


def write_root_index(config):
    source = (PROJECT_PUBLIC_DIR / "index.html").read_text(encoding="utf-8")
    source = source.replace('href="icons/icon.svg"', 'href="icons/web-icon.svg"')
    source = source.replace('href="icons/icon-180.png"', 'href="icons/web-icon-180.png"')
    script = static_config_script(config)
    stylesheet = '    <link rel="stylesheet" href="styles.css" />'
    app_script = '    <script src="app.js" defer></script>'

    if stylesheet in source:
        source = source.replace(stylesheet, script + stylesheet, 1)
    elif app_script in source:
        source = source.replace(app_script, script + app_script, 1)
    else:
        source = source.replace("  </head>", script + "  </head>", 1)

    (BASE_DIR / "index.html").write_text(source, encoding="utf-8")


def write_root_manifest():
    manifest = json.loads((PROJECT_PUBLIC_DIR / "manifest.webmanifest").read_text(encoding="utf-8"))
    manifest["start_url"] = "./"
    manifest["scope"] = "./"
    manifest["short_name"] = "Armario Web"
    manifest["icons"] = [
        {
            "src": "icons/web-icon.svg",
            "sizes": "any",
            "type": "image/svg+xml",
            "purpose": "any",
        },
        {
            "src": "icons/web-icon-180.png",
            "sizes": "180x180",
            "type": "image/png",
            "purpose": "any",
        },
        {
            "src": "icons/web-icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable",
        },
        {
            "src": "icons/web-icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable",
        },
    ]
    write_json(BASE_DIR / "manifest.webmanifest", manifest)


def sync_root_assets():
    shutil.copy2(PROJECT_PUBLIC_DIR / "app.js", BASE_DIR / "app.js")
    shutil.copy2(PROJECT_PUBLIC_DIR / "styles.css", BASE_DIR / "styles.css")

    icons_target = BASE_DIR / "icons"
    if icons_target.exists():
        shutil.rmtree(icons_target)
    write_web_icons(icons_target)


def write_root_pages_files():
    catalog, image_paths = build_catalog("Roupinhas")
    catalog_json = json.dumps(catalog, ensure_ascii=False, sort_keys=True)
    build_id = hashlib.sha256(catalog_json.encode("utf-8")).hexdigest()[:12]
    app_assets = [
        "./",
        "./index.html",
        "./app.js",
        "./styles.css",
        "./app-config.json",
        "./manifest.webmanifest",
        "./icons/web-icon.svg",
        "./icons/web-icon-180.png",
        "./icons/web-icon-192.png",
        "./icons/web-icon-512.png",
    ]

    config = static_runtime_config(catalog["generatedAt"])

    sync_root_assets()
    write_root_index(config)
    write_root_manifest()
    write_json(BASE_DIR / "catalog.json", catalog)
    write_static_config(BASE_DIR, config)
    write_static_service_worker(BASE_DIR, build_id, image_paths, app_assets=app_assets)
    (BASE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    return catalog, image_paths


def main():
    if not PROJECT_PUBLIC_DIR.exists():
        raise RuntimeError("Diretorio project/public nao encontrado.")

    root_catalog, root_images = write_root_pages_files()

    print(
        "Arquivos de GitHub Pages gerados na raiz "
        f"com {len(root_catalog['folders'])} pastas e {len(root_images)} imagens."
    )


if __name__ == "__main__":
    main()
