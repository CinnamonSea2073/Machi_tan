
# Machi_tan（まちたん）

ローカルで Docker による起動が可能な FastAPI のサンプルプロジェクトです。シンプルなフロントエンド（script-tag Vue）と、SQLite を使ったバックエンド API を備えています。Cloudflare Tunnel（cloudflared）を使って外部公開するためのテンプレートも含みます。

主な特徴
- FastAPI ベースの API サーバ
- フロントエンド：ルート `/` に簡易な Vue（script tag）ページ
- データ保存：SQLite（data/app.db）
- ルーティング分離：users / courses / class_course / status / comments / groq などのモジュール化されたルータ
- Groq（チャット生成 / 音声文字起こし）との統合ポイント（`.env` に `GROQ_API_KEY` を置くだけで有効化）
- Docker / Docker Compose で簡単起動

注意点
- 本リポジトリは学習・プロトタイプ用途を想定しています。実運用では DB を PostgreSQL 等に移行し、認証・マイグレーション・セキュリティ対策を導入してください。

目次
- 構成（主なファイル）
- 必要条件
- 起動方法（Docker 推奨）
- 環境変数（.env）
- Groq（外部 API）有効化
- API エンドポイント一覧
- テスト
- 開発メモ / 今後の改善案

構成（主なファイル）
- `Dockerfile` - アプリケーションイメージの定義
- `docker-compose.yml` - `web`（FastAPI）と `cloudflared`（Cloudflare Tunnel）のサービス定義
- `requirements.txt` - Python 依存パッケージ（`groq` / `python-dotenv` を含む）
- `app/` - アプリ本体
  - `app/main.py` - FastAPI アプリ起動・ルータ登録
  - `app/db.py` - SQLite 接続・スキーマ初期化（起動時に自動で作成）
  - `app/groq_client.py` - `.env` から `GROQ_API_KEY` を読んで Groq クライアントを返すラッパー
  - `app/routers/*` - 各種 API ルータ（users, courses, class_course, status, comments, groq, frontend など）
- `data/` - 実行時に `app.db` が作成されます（コミットしないでください）
- `cloudflared/` - Cloudflare トンネル設定テンプレート
- `.env.example` - 環境変数のサンプル（実運用では `.env` にキーを置き、`.env` はコミットしない）

必要条件
- Docker と Docker Compose
- （ローカルで直接実行する場合）Python 3.11

起動手順（Docker 推奨）
1. リポジトリをクローン
2. `.env` を作成（必要に応じて `GROQ_API_KEY` を設定）
   例（ルートに `.env` を作る）:
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

3. Docker Compose で起動（PowerShell の例）
   docker compose up --build

4. 起動確認
   - フロントエンド: http://localhost:8000/
   - API: http://localhost:8000/api/
   - ヘルスチェック: http://localhost:8000/healthz

Cloudflare Tunnel（任意）
- `cloudflared` コンテナは `./cloudflared` ディレクトリを `/etc/cloudflared` にマウントします。
- 実際にトンネルを使う場合は `cloudflared/credentials.json` と `cloudflared/config.yml` を用意してください（credentials.json は機密なのでコミットしないでください）。
- GitHub Actions での利用を想定したテンプレートも含まれています（CI 実行時にシークレットから `credentials.json` を書き出す方法を採用してください）。

環境変数（.env）
- CLOUDFLARE_TUNNEL_ID, CLOUDFLARE_TOKEN - Cloudflare 関連（任意）
- GROQ_API_KEY - Groq API のキー（有効化すると `/api/groq/*` エンドポイントが実際に Groq を呼びます）

Groq の有効化
- `app/groq_client.py` は `.env` から `GROQ_API_KEY` を読み取り、キーがあれば Groq クライアントを返します。
- `app/routers/groq.py` の `/api/groq/text` と `/api/groq/audio` は、キーがある場合に実際に Groq の API を呼び出します。キーがない場合は決定的なフォールバック (テスト用の静的レスポンス) を返し、いずれの場合も `groq_logs` テーブルに記録します。

API（抜粋）
- GET /healthz
- GET /
- POST /api/users - ユーザー作成（UUID を返す）
- POST /api/courses - コース登録（GPX を JSON もしくは multipart で受け付け）
- GET /api/courses
- POST /api/class_course/set - 当日のコースを設定
- GET /api/class_course
- POST /api/status - ステータス追加
- GET /api/status
- POST /api/comments - コメント作成（サーバー側で comment_id を発行）
- GET /api/comments
- POST /api/groq/text - テキストから Groq チャットを呼ぶ
- POST /api/groq/audio - 音声ファイルを送って文字起こし

（詳しいリクエスト/レスポンスは `app/routers` 内の各ファイルを参照してください）

テスト
- pytest ベースのテストを用意しています。
- ローカルで実行する場合:
  - 依存関係をインストールして `pytest` を実行
- Docker 環境では、コンテナ起動後に別端末から:
  docker compose exec web pytest

開発メモ / 今後の改善案
- SQLite を本番向けの DB（Postgres 等）に移行する（マイグレーション導入）
- ユーザー認証（JWT 等）の導入
- Groq レスポンスの厳密なパースとリトライ/エラーハンドリング
- Cloudflare の運用手順（DNS 自動化、証明書管理）

---

作業完了: README を日本語で更新しました。


