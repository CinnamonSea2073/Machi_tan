
# 🗾 Machi_tan（まちたん）- GPS アートアプリ

まちたんは、GPSを使った位置情報ゲームのWebアプリケーションです。小学生のためのまち探検アプリですが、ただのまち探検アプリではありません。GPS機能を用いて移動した軌跡を地図上に記録し、絵や文字を描く「GPSアート」をルートに含めて歩きます。そうすると、普段とは違った道の通り方をして、新たな地域を発見することに繋がります。

## 主な特徴

### 教育機能
- **ステータス制御システム**: 教師が授業の進行（デバッグ→チュートリアル→実行中→終了→結果）を一元管理
- **リアルタイム進捗監視**: 学生の位置情報や活動状況をリアルタイムで確認
- **インタラクティブ チュートリアル**: Leaflet地図を使った段階的な使い方ガイド

### 学生向けPWA
- **PWA対応**: ホーム画面に追加してネイティブアプリのように使用可能
- **オフライン対応**: Service Workerによるキャッシュとオフライン機能
- **音声録音機能**: Groq AIによる音声認識と文字起こし
- **GPS追跡**: リアルタイムでの位置情報記録とルート表示

### 技術スタック
- **バックエンド**: FastAPI + SQLite
- **フロントエンド**: Vue 3 + Vite (PWA)
- **地図**: Leaflet.js
- **AI**: Groq API (音声認識・チャット)
- **アニメーション**: Lottie
- **デプロイ**: Docker + Cloudflare Pages

## プロジェクト構成

## 目次
- [プロジェクト構成](#-プロジェクト構成)
- [セットアップ](#-セットアップ)
- [開発環境](#-開発環境)
- [本番デプロイ](#-本番デプロイ)
- [API エンドポイント](#-api-エンドポイント)
- [PWA機能](#-pwa機能)
- [テスト](#-テスト)
- [ライセンス](#-ライセンス)

```
Machi_tan/
├── 📁 app/                     # FastAPI バックエンド
│   ├── main.py                 # アプリケーションエントリーポイント
│   ├── db.py                   # データベース設定・スキーマ
│   ├── groq_client.py          # Groq AI クライアント
│   ├── routers/                # API ルーター
│       ├── users.py            # ユーザー管理
│       ├── courses.py          # コース管理
│       ├── class_course.py     # クラス・コース連携
│       ├── status.py           # ステータス制御
│       ├── comments.py         # コメント機能
│       ├── comments_new.py     # 新コメント機能
│       ├── groq.py             # AI 統合
│       ├── students.py         # 学生管理
│       ├── control.py          # 教師制御
│       ├── frontend.py         # レガシーフロントエンド
│       └── backend.py          # レガシーバックエンド
│   └── static/                 # レガシー静的ファイル
│       ├── teacher.html        # レガシー教師画面
│       ├── student.html        # レガシー学生画面
│       ├── student_legacy.html # 旧学生画面
│       ├── style.css           # レガシースタイル
│       └── common.js           # 共通JavaScript
│
├── 📁 machi-vue/               # Vue 3 PWA フロントエンド
│   ├── src/
│   │   ├── App.vue             # メインアプリケーション
│   │   ├── main.js             # エントリーポイント
│   │   ├── style.css           # グローバルスタイル
│   │   ├── components/         # Vue コンポーネント
│   │   │   ├── TutorialScreen.vue    # チュートリアル画面
│   │   │   ├── TeacherScreen.vue     # 教師制御画面
│   │   │   ├── LoadingScreen.vue     # ローディング画面
│   │   │   ├── MapScreen.vue         # マップ画面
│   │   │   ├── ResultScreen.vue      # 結果表示画面
│   │   │   ├── NameInputForm.vue     # 名前入力フォーム
│   │   │   ├── CharacterContainer.vue # キャラクターアニメーション
│   │   │   ├── TransceiverButton.vue # 音声録音ボタン
│   │   │   ├── TransceiverSvg.vue    # 無線機SVGアイコン
│   │   │   ├── VoiceButton.vue       # 音声ボタン
│   │   │   ├── TutorialBubble.vue    # チュートリアル吹き出し
│   │   │   ├── DebugPanel.vue        # デバッグパネル
│   │   │   └── APITest.vue           # API テストコンポーネント
│   │   ├── composables/        # Vue Composition API
│   │   │   ├── useStatusControl.js   # ステータス制御
│   │   │   ├── useVoiceRecording.js  # 音声録音・AI処理
│   │   │   ├── useTutorial.js        # チュートリアル制御
│   │   │   └── useLottieAnimations.js # アニメーション
│   │   └── config/
│   │       └── api.js          # API 設定
│   ├── public/                 # 静的ファイル・PWA アセット
│   │   ├── icon.svg            # アプリアイコン（ソース）
│   │   ├── pwa-192x192.png     # PWA アイコン 192x192
│   │   ├── pwa-512x512.png     # PWA アイコン 512x512
│   │   ├── apple-touch-icon-180x180.png # Apple touch アイコン
│   │   └── favicon.ico         # ファビコン
│   ├── dist/                   # ビルド成果物
│   ├── vite.config.js          # Vite + PWA 設定
│   ├── pwa-assets.config.json  # PWA アセット生成設定
│   ├── generate-icons.js       # アイコン生成スクリプト
│   └── package.json            # Node.js 依存関係
│
├── 📁 cloudflared/             # Cloudflare Tunnel 設定
│   └── config.yml              # Tunnel 設定ファイル
├── 📁 data/                    # SQLite データベース（実行時作成）
├── 📁 tests/                   # テストファイル
│   ├── test_basic.py           # 基本機能テスト
│   └── test_new_endpoints.py   # 新規エンドポイントテスト
├── 📁 scripts/                 # ユーティリティスクリプト
│   └── dump_groq_logs.py       # Groq ログ抽出
├── Dockerfile                  # マルチステージ Docker ビルド
├── docker-compose.yml          # サービス構成
├── requirements.txt            # Python 依存関係
├── .dockerignore              # Docker ビルド除外設定
├── sample_course.gpx          # サンプルコースファイル
├── test_course.gpx            # テスト用コースファイル
└── README.md                  # このファイル
```

## セットアップ

### 必要条件
- **Docker** と **Docker Compose** （推奨）
- または **Node.js 18+** と **Python 3.11+** （開発環境）

### Docker での起動（推奨）

1. **リポジトリをクローン**
```bash
git clone https://github.com/CinnamonSea2073/Machi_tan.git
cd Machi_tan
```

2. **環境変数を設定**
```bash
# .env ファイルを作成
cp .env.example .env
# GROQ_API_KEY を設定（音声認識機能を使う場合）
```

3. **アプリケーションを起動**
```bash
docker compose up --build
```

4. **アクセス確認**
- **教師用画面（レガシー）**: http://localhost:8000/app?mode=teacher
- **学生用PWA**: http://localhost:8000/app/
- **API ドキュメント**: http://localhost:8000/docs
- **ヘルスチェック**: http://localhost:8000/healthz

## 💻 開発環境

### Vue.js 開発サーバー
```bash
cd machi-vue
npm install
npm run dev
# http://localhost:5173 でアクセス
```

### FastAPI 開発サーバー
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# http://localhost:8000 でアクセス
```

### 環境変数（.env）
```bash
# Groq AI（音声認識・チャット）
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Cloudflare Tunnel（任意）
CLOUDFLARE_TUNNEL_ID=your-tunnel-id
CLOUDFLARE_TOKEN=your-token
```

## システム動作フロー

1. **教師がステータスを「チュートリアル」に設定**
2. **学生がPWAアプリでチュートリアルを受講**
   - インタラクティブな地図操作ガイド
   - 段階的な機能説明
3. **ステータス「実行中」で実際のGPSアート作成**
   - リアルタイム位置追跡
   - 音声コメント録音
   - Groq AIによる音声認識
4. **ステータス「結果」で成果確認**
   - 個人統計表示
   - 歩行距離・ルート表示
   - コメント履歴
5. **ステータス「デバッグ」で開発を推奨**

## API エンドポイント

### 認証・ユーザー管理
- `POST /api/users` - ユーザー作成（UUID発行）
- `GET /api/students` - 学生一覧取得

### コース・クラス管理
- `POST /api/courses` - コース登録（GPX対応）
- `GET /api/courses` - コース一覧
- `POST /api/class_course/set` - 当日コース設定
- `GET /api/class_course` - クラスコース取得

### ステータス制御（教師用）
- `POST /api/status` - ステータス更新
- `GET /api/status` - 現在ステータス取得
- ステータス種類: `デバッグ` / `チュートリアル` / `実行中` / `終了` / `結果`

### コメント・音声機能
- `POST /api/comments` - コメント投稿
- `GET /api/comments` - コメント取得
- `POST /api/groq/audio` - 音声ファイル → 文字起こし
- `POST /api/groq/text` - テキスト → AI チャット

### 静的ファイル
- `/static/*` - FastAPI 静的ファイル
- `/app/*` - Vue PWA アプリケーション

詳細なリクエスト/レスポンス仕様は `/docs` （FastAPI自動生成ドキュメント）を参照してください。

## PWA機能

### 主要機能
- **ホーム画面追加**: ネイティブアプリのようにインストール可能
- **オフライン対応**: Service Workerによるキャッシュ
- **フルスクリーン**: 余計なUIを排除した上での体験
- **通知対応**: 将来的な拡張に対応
- **レスポンシブ**: モバイル・タブレット・デスクトップ対応

### デザインシステム
- **カラーテーマ**: `#FFB143` （オレンジ系）
- **アイコン**: カスタム SVG アイコン（公式PWAアセットジェネレーターで自動生成）
- **アニメーション**: Lottie による滑らかなキャラクターアニメーション
- **フォント**: システムフォント使用

## テスト

### Python バックエンドテスト
```bash
# ローカル環境
pip install -r requirements.txt
pytest

# Docker 環境
docker compose exec web pytest
```

