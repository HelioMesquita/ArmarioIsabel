#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
WARDROBE_PATHSPEC = "roupinhas"
COMMIT_MESSAGE = "nova foto adicionada"
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
GENERATED_PATHS = [
    ".nojekyll",
    "app-config.json",
    "app.js",
    "catalog.json",
    "icons",
    "index.html",
    "manifest.webmanifest",
    "styles.css",
    "sw.js",
]


def git_command(arguments):
    return ["git", "-c", f"safe.directory={BASE_DIR}", *arguments]


def run(command):
    result = subprocess.run(command, cwd=BASE_DIR)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def git_null_paths(arguments):
    result = subprocess.run(
        git_command(arguments),
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        check=True,
    )
    output = result.stdout.decode("utf-8", errors="replace")
    return [path for path in output.split("\0") if path]


def is_wardrobe_image(path):
    relative_path = Path(path)
    return (
        len(relative_path.parts) > 1
        and relative_path.parts[0] == WARDROBE_PATHSPEC
        and relative_path.suffix.lower() in IMAGE_EXTENSIONS
    )


def changed_image_paths():
    candidates = set()
    queries = [
        ["ls-files", "--others", "--exclude-standard", "-z", "--", WARDROBE_PATHSPEC],
        ["diff", "--name-only", "-z", "--diff-filter=AMR", "--", WARDROBE_PATHSPEC],
        ["diff", "--name-only", "-z", "--cached", "--diff-filter=AMR", "--", WARDROBE_PATHSPEC],
    ]

    for query in queries:
        candidates.update(git_null_paths(query))

    return sorted(path for path in candidates if is_wardrobe_image(path))


def has_staged_changes(paths):
    result = subprocess.run(
        git_command(["diff", "--cached", "--quiet", "--", *paths]),
        cwd=BASE_DIR,
    )
    if result.returncode == 0:
        return False
    if result.returncode == 1:
        return True
    raise SystemExit(result.returncode)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publica fotos novas do armario, faz commit e envia para o remoto."
    )
    parser.add_argument(
        "-m",
        "--message",
        default=COMMIT_MESSAGE,
        help=f"Mensagem do commit. Padrao: {COMMIT_MESSAGE!r}.",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Faz o commit, mas nao executa git push.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    image_paths = changed_image_paths()

    if not image_paths:
        print("Nenhuma foto nova ou alterada em roupinhas/. Nada para publicar.")
        return

    print("Fotos que entram nesta publicacao:")
    for path in image_paths:
        print(f"- {path}")

    run([sys.executable, "scripts/publish_static.py"])

    paths_to_commit = sorted(set(image_paths + GENERATED_PATHS))
    run(git_command(["add", "--", *paths_to_commit]))

    if not has_staged_changes(paths_to_commit):
        print("Nada mudou depois de gerar a versao estatica. Commit cancelado.")
        return

    run(git_command(["commit", "-m", args.message, "--", *paths_to_commit]))

    if args.no_push:
        print("Commit criado. Push pulado por causa de --no-push.")
        return

    run(git_command(["push"]))
    print("Foto publicada, commit criado e push concluido.")


if __name__ == "__main__":
    main()
