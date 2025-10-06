# Vue.js リファクタリング実行プラン
**現実的・段階的・非破壊的モダン化計画**

## 📊 現状分析

### コードベース規模
- **student.html**: 975行（チュートリアル、地図、音声認識統合）
- **teacher.html**: 381行（Vue.js使用済み、管理画面）  
- **既存機能**: 完全動作、本番運用可能

### 技術スタック現況
- **フロントエンド**: HTML/CSS/JS + Leaflet + Lottie
- **バックエンド**: FastAPI + SQLite
- **実装済み**: PWA基盤、音声認識、Lottieアニメーション、地図システム

## 🎯 リファクタリング戦略

### **Stage 0: 準備・検証フェーズ（1週間）**
> 既存機能を破壊せずにVue環境を構築

#### **0.1 Vue開発環境構築**
```bash
# 新しいVueプロジェクト作成（student.htmlと並行運用）
npm create vue@latest machi-vue
cd machi-vue
npm install
npm install leaflet lottie-web
```

#### **0.2 既存HTMLのバックアップとドキュメント化**
- `student.html` → `student_legacy.html` 
- 全機能の動作確認チェックリスト作成
- APIエンドポイント一覧抽出

#### **0.3 Vue移行テンプレート作成**
```javascript
// vue-config.js - 既存FastAPIと統合
export default {
  devServer: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/static': 'http://localhost:8000'
    }
  }
}
```

**成果物**: Vue開発環境 + 既存システム並行稼働

---

### **Stage 1: 基盤移行フェーズ（2週間）**
> 既存機能を1:1でVueコンポーネント化

#### **1.1 基本レイアウト移行**
```vue
<!-- App.vue -->
<template>
  <div id="app">
    <TutorialScreen v-if="showTutorial" />
    <MapScreen v-else />
    <VoiceButton v-if="!showTutorial" />
    <DebugPanel v-if="debugMode" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TutorialScreen from './components/TutorialScreen.vue'
import MapScreen from './components/MapScreen.vue'
// 既存のlocalStorage チェックロジックをそのまま移植
</script>
```

#### **1.2 チュートリアルシステム移行**
```vue
<!-- components/TutorialScreen.vue -->
<template>
  <div class="tutorial-screen">
    <TutorialBubble 
      :message="currentStep.message"
      :character="currentStep.character"
    />
    <CharacterContainer :animation-url="currentStep.character" />
    <NameInputForm v-if="currentStep.isNameInput" @submit="handleNameSubmit" />
  </div>
</template>

<script setup>
// 既存のtutorialStory配列をそのまま使用
// preloadAllAnimations()関数を移植
const tutorialStory = [/* 既存の10ステップデータ */]
</script>
```

#### **1.3 地図システム移行**
```vue
<!-- components/MapScreen.vue -->
<template>
  <div id="map" ref="mapContainer"></div>
</template>

<script setup>
import L from 'leaflet'
import { ref, onMounted, onUnmounted } from 'vue'

// 既存のinitMap()関数を移植
// routeCoords, evaluateProximity()等をそのまま使用
</script>
```

**成果物**: Vue版基本機能（チュートリアル + 地図）

---

### **Stage 2: 高度機能移行フェーズ（2週間）**
> 音声認識・Lottieアニメーション・リアルタイム機能

#### **2.1 音声認識システム移行**
```vue
<!-- composables/useVoiceRecording.js -->
export function useVoiceRecording() {
  const isRecording = ref(false)
  
  // 既存のMediaRecorder + analyser ロジックを移植
  const startRecording = async () => {
    // 既存のstartRecording()関数内容
  }
  
  const stopRecording = async () => {  
    // 既存のstopRecording()関数内容
  }
  
  return { isRecording, startRecording, stopRecording }
}
```

#### **2.2 Lottieアニメーションシステム移行**
```vue
<!-- components/CharacterContainer.vue -->
<template>
  <div ref="lottieContainer" class="character-container"></div>
</template>

<script setup>
import lottie from 'lottie-web'
// 既存のpreloadedAnimations, switchToCharacter()を移植
</script>
```

#### **2.3 リアルタイム通信移行**
```javascript
// composables/useComments.js
export function useComments() {
  // 既存のsaveComment(), pollNewComments()を移植
  // addCommentMarker()をVue reactiveに適応
}
```

**成果物**: 全機能Vue移行完了

---

### **Stage 3: UX向上フェーズ（1週間）**
> Vue固有の機能でユーザー体験向上

#### **3.1 トランジション追加**
```vue
<template>
  <Transition name="bubble" appear>
    <TutorialBubble v-if="showBubble" />
  </Transition>
  
  <Transition name="slide" mode="out-in">
    <TutorialScreen v-if="showTutorial" key="tutorial" />
    <MapScreen v-else key="map" />
  </Transition>
</template>

<style>
.bubble-enter-active { transition: all 0.4s cubic-bezier(.22,.9,.5,1) }
.bubble-enter-from { transform: scale(0.95); opacity: 0 }
.slide-enter-active, .slide-leave-active { transition: all 0.3s }
.slide-enter-from { transform: translateX(100%) }
.slide-leave-to { transform: translateX(-100%) }
</style>
```

#### **3.2 PWA機能強化**
```javascript
// public/manifest.json 改善
{
  "name": "まちたん",
  "short_name": "まちたん", 
  "display": "standalone",
  "theme_color": "#1976d2",
  "icons": [/* アプリアイコン追加 */]
}

// Service Worker強化（vite-plugin-pwa使用）
```

**成果物**: スムーズなアニメーション + PWA体験

---

### **Stage 4: 本番移行フェーズ（1週間）**
> 安全な本番デプロイとフォールバック

#### **4.1 段階的デプロイ**
```nginx
# nginx設定（A/Bテスト対応）
location / {
  if ($cookie_use_vue = "true") {
    try_files $uri /vue/index.html;
  }
  try_files $uri /legacy/student.html;
}
```

#### **4.2 パフォーマンス最適化**
```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'leaflet': ['leaflet'],
          'lottie': ['lottie-web']
        }
      }
    }
  }
}
```

**成果物**: 本番Vue版 + レガシー版並行運用

---

## 🛡️ リスク軽減策

### **機能破壊防止**
- 各Stageで全機能テスト実行
- レガシー版を常にフォールバック用に維持
- APIエンドポイント変更なし（既存FastAPI継続使用）

### **開発効率確保**
- 既存JavaScriptロジックの最大限活用
- 段階的移行（一度に全て書き換えない）
- コンポーネント単位でのテスト可能

### **運用継続性**
```javascript
// 緊急時フォールバック
if (vueAppFailed) {
  window.location.href = '/student_legacy.html'
}
```

## 📈 期待効果

### **短期（移行完了時）**
- ✅ 既存機能100%維持
- ✅ スムーズなページ遷移
- ✅ 改善されたチュートリアル体験

### **中長期（移行後3ヶ月）**
- 🚀 新機能開発速度向上（Vue Reactivity活用）
- 🔧 保守性向上（コンポーネント分割）
- 📱 PWA体験向上（オフライン対応強化）

## ⚡ 実行開始手順

### **今すぐ開始可能**
```bash
# 1. Vue環境構築
cd /path/to/Machi_tan
npm create vue@latest machi-vue
cd machi-vue
npm install leaflet lottie-web

# 2. 開発サーバー起動
npm run dev  # Vue: http://localhost:5173
# 別ターミナルで既存FastAPI継続: http://localhost:8000
```

### **週次マイルストーン**
- **Week 1**: Stage 0完了（Vue環境+既存HTML並行）
- **Week 3**: Stage 1完了（基本Vue移行）
- **Week 5**: Stage 2完了（全機能移行）
- **Week 6**: Stage 3完了（UX向上）
- **Week 7**: Stage 4完了（本番デプロイ）

---

## 🔄 継続的改善計画

### **移行後の発展**
1. **TypeScript導入**（任意、段階的）
2. **Pinia状態管理**（複雑性増加時）  
3. **Vitest単体テスト**（品質保証）
4. **Storybook**（コンポーネントドキュメント）

### **技術負債解消**
- 975行のHTMLから構造化されたVueコンポーネントへ
- グローバル変数から組織化されたComposablesへ
- インラインスタイルからscoped CSSへ

---

**この計画の特徴**: 既存機能を一切破壊せず、段階的にモダン化を実現。各段階で動作するシステムを維持し、リスクを最小化しながら確実にVue.jsへ移行。**

## 🎯 判定：実行推奨

現在のコードベースの複雑さと完成度を考慮すると、この段階的Vue移行アプローチが最も現実的です。既存の高品質な機能（チュートリアル、音声認識、Lottieアニメーション）を保持しながら、モダンな開発体験と保守性を獲得できます。