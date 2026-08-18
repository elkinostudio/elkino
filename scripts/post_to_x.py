"""
post_to_x.py
------------
data/content.json の動画一覧を見て、まだXに告知していない新着動画があれば自動投稿する。
一度投稿した動画IDは data/posted_state.json に記録し、二重投稿を防ぐ。

必要な環境変数（すべて X Developer Portal のアプリから取得。自分のアカウント専用なので
OAuthの認証フローは不要 — アプリ作成時に「Read and Write」権限でアクセストークンを発行するだけでよい）:
  X_API_KEY
  X_API_SECRET
  X_ACCESS_TOKEN
  X_ACCESS_TOKEN_SECRET

注意（コストについて）:
  2026年2月以降、X APIは従量課金制。URL付き投稿は1件あたり約$0.20。
  月に数本の新着動画を告知する程度であれば、月額は数百円〜千円程度に収まる見込み。
  無料ではないが、個人利用として現実的な金額。

使い方:
  python scripts/post_to_x.py
"""

import json
import os
import sys
from pathlib import Path

import tweepy

ROOT = Path(__file__).resolve().parent.parent
CONTENT_PATH = ROOT / "data" / "content.json"
STATE_PATH = ROOT / "data" / "posted_state.json"


def load_state() -> set[str]:
    if STATE_PATH.exists():
        with open(STATE_PATH, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_state(posted_ids: set[str]) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(posted_ids), f, ensure_ascii=False, indent=2)


def build_post_text(video: dict) -> str:
    text = f"新しい動画を公開しました。\n\n{video['title']}\n\n{video['url']}"
    return text[:280]


def main() -> None:
    required_env = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
    missing = [k for k in required_env if not os.environ.get(k)]
    if missing:
        sys.exit(f"環境変数が不足しています: {', '.join(missing)}")

    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    with open(CONTENT_PATH, encoding="utf-8") as f:
        content = json.load(f)

    all_videos = [v for channel in content["channels"] for v in channel["videos"]]

    posted_ids = load_state()
    new_videos = [v for v in all_videos if v["video_id"] not in posted_ids]

    if not new_videos:
        print("新着動画はありません。投稿はスキップします。")
        return

    for video in new_videos:
        text = build_post_text(video)
        try:
            client.create_tweet(text=text)
            posted_ids.add(video["video_id"])
            print(f"[OK] Xに投稿しました: {video['title']}")
        except Exception as e:
            print(f"[WARN] 投稿に失敗しました（{video['title']}）: {e}", file=sys.stderr)

    save_state(posted_ids)


if __name__ == "__main__":
    main()
