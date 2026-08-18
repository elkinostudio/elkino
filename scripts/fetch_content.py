"""
fetch_content.py
----------------
YouTube（複数チャンネル）と note の最新投稿を取得し、data/content.json に保存する。

必要な環境変数:
  YOUTUBE_API_KEY   - Google Cloud Console で取得した YouTube Data API v3 のAPIキー（無料枠あり）

使い方:
  python scripts/fetch_content.py

設計メモ（Python簡略化ポイント）:
  - YouTube検索は search.list ではなく、channels.list + playlistItems.list を使う。
    search.list は1回100ユニット消費するが、この方法なら1回1ユニットで済み、
    無料クォータ（1日10,000ユニット）を無駄にしない。
"""

import json
import os
import sys
from pathlib import Path

import feedparser
import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"
OUTPUT_PATH = ROOT / "data" / "content.json"

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"config.yaml が見つかりません。config.yaml.example をコピーして作成してください: {CONFIG_PATH}"
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_uploads_playlist_id(channel_id: str, api_key: str) -> str:
    """チャンネルIDから「アップロード動画」プレイリストIDを取得する（1ユニット消費）。"""
    resp = requests.get(
        f"{YOUTUBE_API_BASE}/channels",
        params={"part": "contentDetails", "id": channel_id, "key": api_key},
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        raise ValueError(f"チャンネルが見つかりません: {channel_id}")
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_latest_videos(channel_name: str, channel_id: str, api_key: str, max_results: int) -> list[dict]:
    uploads_playlist_id = get_uploads_playlist_id(channel_id, api_key)
    resp = requests.get(
        f"{YOUTUBE_API_BASE}/playlistItems",
        params={
            "part": "snippet",
            "playlistId": uploads_playlist_id,
            "maxResults": max_results,
            "key": api_key,
        },
        timeout=15,
    )
    resp.raise_for_status()
    videos = []
    for item in resp.json().get("items", []):
        snippet = item["snippet"]
        video_id = snippet["resourceId"]["videoId"]
        thumbnails = snippet.get("thumbnails", {})
        thumb = thumbnails.get("maxres") or thumbnails.get("high") or thumbnails.get("medium") or {}
        videos.append(
            {
                "channel": channel_name,
                "title": snippet["title"],
                "published_at": snippet["publishedAt"],
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": thumb.get("url", ""),
            }
        )
    return videos


def get_latest_note_posts(username: str, max_posts: int) -> list[dict]:
    """note.com は各ユーザーに公式RSSフィードがあるため、APIキー不要で取得できる。"""
    feed_url = f"https://note.com/{username}/rss"
    feed = feedparser.parse(feed_url)
    posts = []
    for entry in feed.entries[:max_posts]:
        posts.append(
            {
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "published_at": entry.get("published", ""),
                "summary": entry.get("summary", "")[:200],
            }
        )
    return posts


def main() -> None:
    config = load_config()
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        sys.exit("環境変数 YOUTUBE_API_KEY が設定されていません。")

    all_videos = []
    for ch in config["youtube"]["channels"]:
        try:
            videos = get_latest_videos(
                ch["name"], ch["channel_id"], api_key, config["youtube"]["max_videos_per_channel"]
            )
            all_videos.extend(videos)
            print(f"[OK] {ch['name']}: {len(videos)}件取得")
        except Exception as e:
            print(f"[WARN] {ch['name']} の取得に失敗: {e}", file=sys.stderr)

    all_videos.sort(key=lambda v: v["published_at"], reverse=True)

    note_posts = []
    try:
        note_posts = get_latest_note_posts(config["note"]["username"], config["note"]["max_posts"])
        print(f"[OK] note: {len(note_posts)}件取得")
    except Exception as e:
        print(f"[WARN] note の取得に失敗: {e}", file=sys.stderr)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"videos": all_videos, "note_posts": note_posts}, f, ensure_ascii=False, indent=2)

    print(f"content.json を書き出しました: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
