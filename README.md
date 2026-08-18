# elkino studio Portfolio Site

YouTube（複数チャンネル）と note の最新投稿を自動取得し、GitHub Pages 上のポートフォリオサイトを
自動更新する仕組み一式です。GitHub Actions が6時間ごとに実行され、新着があればサイトを再生成し、
新しい動画があればXにも自動投稿します。

## 全体の仕組み

```
GitHub Actions（6時間ごと）
  → scripts/fetch_content.py   … YouTube / note の最新情報を取得 → data/content.json
  → scripts/build_site.py      … content.json からサイトを生成 → public/
  → scripts/post_to_x.py       … 新着動画があればXに告知（任意・不要なら削除可）
  → public/ を gh-pages ブランチにデプロイ → GitHub Pagesで公開
```

## あなたが行う作業（一度だけ）

### 1. GitHubリポジトリを作る
1. github.com で新規リポジトリを作成（Public推奨。Privateでも動くが、Actionsの無料枠が
   Publicほど潤沢ではない）
2. このフォルダの中身をすべてそのリポジトリにpush

### 2. config.yaml を作る
`config.yaml.example` をコピーして `config.yaml` という名前にし、
- YouTubeチャンネルID（2つ）
- noteのユーザー名
を実際の値に書き換えてください。チャンネルIDに秘密情報はないので、そのままコミットして大丈夫です。

チャンネルIDの調べ方：チャンネルページ → 概要 → 「チャンネルアカウント」共有 → コピーすると
`UC` から始まるIDが取れます。

### 3. YouTube Data API キーを取得（無料）
1. https://console.cloud.google.com にアクセス
2. 新規プロジェクトを作成
3. 「APIとサービス」→「ライブラリ」→ "YouTube Data API v3" を有効化
4. 「認証情報」→「APIキーを作成」

### 4. （任意）X（旧Twitter）で自動投稿する場合
1. https://developer.x.com でアプリを作成
2. アプリの権限を「Read and Write」に設定
3. Consumer Key / Secret、Access Token / Secret の4つを発行
4. **費用について**：2026年2月以降、Xの投稿APIは従量課金です。URL付き投稿は1件あたり
   約$0.20。月に数本の告知であれば月額は数百円〜千円程度に収まる見込みです。無料ではない点、
   ご了承ください。不要であれば `.github/workflows/update-site.yml` から
   「Post new videos to X」のステップを削除すれば、この部分だけ無効化できます。

### 5. GitHubリポジトリにSecretsを登録
リポジトリの Settings → Secrets and variables → Actions → New repository secret で、
以下を登録：
- `YOUTUBE_API_KEY`（必須）
- `X_API_KEY` / `X_API_SECRET` / `X_ACCESS_TOKEN` / `X_ACCESS_TOKEN_SECRET`（X連携する場合のみ）

### 6. GitHub Pagesを有効化
リポジトリの Settings → Pages → Source を「Deploy from a branch」→ ブランチを `gh-pages` に設定
（最初のActions実行後に `gh-pages` ブランチが作られるので、それまでは選べません。
一度 Actions タブから手動実行 [workflow_dispatch] してから設定してください）

## 手元での動作確認（任意）

```bash
pip install -r requirements.txt
export YOUTUBE_API_KEY="取得したAPIキー"
python scripts/fetch_content.py
python scripts/build_site.py
# public/index.html をブラウザで開いて確認
```

## デザインについて

ダークトーンの静かな画面、映像サムネイルは白黒からホバーで色が戻る演出、スクロールで
少しずつ現れる控えめなアニメーションのみを使っています。「語らず、見せる」という
mono Japanの編集方針に合わせ、装飾は最小限にしています。`static/style.css` の
`:root` 内の変数を書き換えれば配色・書体を調整できます。
