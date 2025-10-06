
# 🗾 Machi_tan（まちたん）- GPS アートアプリ

まちたんは、GPSを使った位置情報ゲーム・アートアプリケーションです。学生がチュートリアルを受けながら指定されたルートを歩き、音声コメントを録音して、GPSアートを作成します。教師は授業の進行を制御し、学生の進捗を管理できます。

## 🌟 主な特徴

### 🎓 教育機能
- **ステータス制御システム**: 教師が授業の進行（チュートリアル→実行中→休憩→結果→デバッグ）を一元管理
- **リアルタイム進捗監視**: 学生の位置情報や活動状況をリアルタイムで確認
- **インタラクティブ チュートリアル**: Leaflet地図を使った段階的な使い方ガイド

### 📱 学生向けPWA
- **PWA対応**: ホーム画面に追加してネイティブアプリのように使用可能
- **フルスクリーン表示**: 没入感のある学習体験
- **オフライン対応**: Service Workerによるキャッシュとオフライン機能
- **音声録音機能**: Groq AIによる音声認識と文字起こし
- **GPS追跡**: リアルタイムでの位置情報記録とルート表示

### 🔧 技術スタック
- **バックエンド**: FastAPI + SQLite
- **フロントエンド**: Vue 3 + Vite (PWA)
- **地図**: Leaflet.js
- **AI**: Groq API (音声認識・チャット)
- **アニメーション**: Lottie
- **デプロイ**: Docker + Cloudflare Pages

## 📁 プロジェクト構成

## 📋 目次
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
│   └── routers/                # API ルーター
│       ├── users.py            # ユーザー管理
│       ├── courses.py          # コース管理
│       ├── class_course.py     # クラス・コース連携
│       ├── status.py           # ステータス制御
│       ├── comments.py         # コメント機能
│       ├── groq.py             # AI 統合
│       ├── students.py         # 学生管理
│       ├── control.py          # 教師制御
│       ├── frontend.py         # レガシーフロントエンド
│       └── backend.py          # レガシーバックエンド
│
├── 📁 machi-vue/               # Vue 3 PWA フロントエンド
│   ├── src/
│   │   ├── components/         # Vue コンポーネント
│   │   │   ├── App.vue         # メインアプリケーション
│   │   │   ├── TutorialScreen.vue    # チュートリアル画面
│   │   │   ├── TeacherScreen.vue     # 教師制御画面
│   │   │   ├── LoadingScreen.vue     # ローディング画面
│   │   │   ├── ResultScreen.vue      # 結果表示画面
│   │   │   └── TransceiverButton.vue # 音声録音ボタン
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
│   │   └── apple-touch-icon.png # Apple touch アイコン
│   ├── dist/                   # ビルド成果物
│   ├── vite.config.js          # Vite + PWA 設定
│   └── package.json            # Node.js 依存関係
│
├── 📁 cloudflared/             # Cloudflare Tunnel 設定
├── 📁 data/                    # SQLite データベース（実行時作成）
├── 📁 tests/                   # テストファイル
├── Dockerfile                  # マルチステージ Docker ビルド
├── docker-compose.yml          # サービス構成
├── requirements.txt            # Python 依存関係
├── .dockerignore              # Docker ビルド除外設定
├── CLOUDFLARE_DEPLOYMENT.md   # デプロイ手順書
└── README.md                  # このファイル
```

## 🚀 セットアップ

### 必要条件
- **Docker** と **Docker Compose** （推奨）
- または **Node.js 18+** と **Python 3.11+** （開発環境）

### 🐳 Docker での起動（推奨）

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
- 🎓 **教師用画面**: http://localhost:8000/
- 📱 **学生用PWA**: http://localhost:8000/app/
- 🔧 **API ドキュメント**: http://localhost:8000/docs
- ❤️ **ヘルスチェック**: http://localhost:8000/healthz

## 💻 開発環境

### Vue.js 開発サーバー
```bash
cd machi-vue
npm install
npm run dev
# http://localhost:5174 でアクセス
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

## 🌐 本番デプロイ

### Cloudflare Pages（PWA）
詳細な手順は `CLOUDFLARE_DEPLOYMENT.md` を参照してください。

```bash
# 1. Vue アプリをビルド
cd machi-vue
npm run build

# 2. dist/ フォルダを Cloudflare Pages にデプロイ
# または GitHub 連携で自動デプロイ
```

### Docker デプロイ
```bash
# マルチステージビルドで本番用イメージを作成
docker build -t machi-tan .

# コンテナ起動
docker run -p 8000:8000 -e GROQ_API_KEY=your-key machi-tan
```

## 🔄 システム動作フロー

1. **👨‍🏫 教師がステータスを「チュートリアル」に設定**
2. **📱 学生がPWAアプリでチュートリアルを受講**
   - インタラクティブな地図操作ガイド
   - 段階的な機能説明
3. **🚶‍♀️ ステータス「実行中」で実際のGPSアート作成**
   - リアルタイム位置追跡
   - 音声コメント録音
   - Groq AIによる音声認識
4. **📊 ステータス「結果」で成果確認**
   - 個人統計表示
   - 歩行距離・ルート表示
   - コメント履歴
5. **🔧 ステータス「デバッグ」で問題解決**

## 🔌 API エンドポイント

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

## 📱 PWA機能

### ✨ 主要機能
- **🏠 ホーム画面追加**: ネイティブアプリのようにインストール可能
- **📵 オフライン対応**: Service Workerによるキャッシュ
- **🖥️ フルスクリーン**: 没入感のある学習体験
- **🔔 通知対応**: 将来的な拡張に対応
- **📐 レスポンシブ**: モバイル・タブレット・デスクトップ対応

### 🎨 デザインシステム
- **カラーテーマ**: `#FFB143` （オレンジ系）
- **アイコン**: カスタム SVG アイコン（408x408px）
- **アニメーション**: Lottie による滑らかなキャラクターアニメーション
- **フォント**: システムフォント使用

## 🧪 テスト

### Python バックエンドテスト
```bash
# ローカル環境
pip install -r requirements.txt
pytest

# Docker 環境
docker compose exec web pytest
```

### Vue フロントエンドテスト
```bash
cd machi-vue
npm run test  # 将来的な実装予定
```

## 🛠️ 開発メモ・今後の改善案

### 📈 優先度高
- [ ] **PostgreSQL移行**: SQLiteから本番向けDB移行
- [ ] **ユーザー認証**: JWT認証システム導入
- [ ] **エラーハンドリング**: Groq API の厳密なパース・リトライ機能
- [ ] **テストカバレッジ**: フロントエンド単体テスト追加

### 🔮 将来的な機能
- [ ] **リアルタイム通信**: WebSocket によるライブ更新
- [ ] **多言語対応**: i18n 国際化対応
- [ ] **データ分析**: 学習効果測定ダッシュボード
- [ ] **マルチテナント**: 複数の学校・クラス対応

### 🔒 セキュリティ
- [ ] **HTTPS強制**: 本番環境でのSSL/TLS実装
- [ ] **CORS設定**: 厳密なオリジン制御
- [ ] **入力検証**: より厳密なバリデーション
- [ ] **レート制限**: API濫用防止

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは教育・研究目的で開発されています。
商用利用については事前にご相談ください。

## 👥 開発チーム

- **CinnamonSea2073** - プロジェクトオーナー・主要開発者

---

**🗾 まちたんで、楽しい GPS アートを体験しよう！**


