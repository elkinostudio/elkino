"""
build_site.py
--------------
data/content.json を templates/index.html.jinja に流し込み、public/index.html を生成する。
static/ の中身（CSS等）も public/ にコピーする。

使い方:
  python scripts/build_site.py
"""

import json
import shutil
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
CONTENT_PATH = ROOT / "data" / "content.json"
CONFIG_PATH = ROOT / "config.yaml"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
PUBLIC_DIR = ROOT / "public"


def main() -> None:
    with open(CONTENT_PATH, encoding="utf-8") as f:
        content = json.load(f)

    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    template = env.get_template("index.html.jinja")

    html = template.render(
        site=config["site"],
        videos=content["videos"],
        note_posts=content["note_posts"],
    )

    PUBLIC_DIR.mkdir(exist_ok=True)
    (PUBLIC_DIR / "index.html").write_text(html, encoding="utf-8")

    if STATIC_DIR.exists():
        dest = PUBLIC_DIR / "static"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(STATIC_DIR, dest)

    print(f"サイトを生成しました: {PUBLIC_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
