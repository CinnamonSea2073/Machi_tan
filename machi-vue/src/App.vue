<template>
  <div id="app">
    <!-- 既存のlocalStorageチェックロジックに基づいて表示切り替え -->
    <TutorialScreen 
      v-if="showTutorial" 
      @complete="handleTutorialComplete"
    />
    <MapScreen v-else />
    <DebugPanel 
      v-if="debugMode" 
      @show-tutorial="showTutorial = true"
      @show-map="showTutorial = false" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TutorialScreen from './components/TutorialScreen.vue'
import MapScreen from './components/MapScreen.vue'
import DebugPanel from './components/DebugPanel.vue'

// 既存のロジックを移植: localStorage チェック
const showTutorial = ref(true)
const debugMode = ref(false)

// チュートリアル完了ハンドラー
const handleTutorialComplete = () => {
  showTutorial.value = false
  console.log('チュートリアル完了、地図画面に移行します')
}

// デバッグモード状態をチェック
const checkDebugMode = async () => {
  try {
    const response = await fetch('/api/status')
    if (response.ok) {
      const data = await response.json()
      debugMode.value = data.status === 'デバッグ'
    }
  } catch (error) {
    console.warn('デバッグモード確認失敗:', error)
  }
}

onMounted(async () => {
  // 既存student.htmlのロジックを移植
  if (localStorage.getItem('studentUuid')) {
    // 既に登録済みの場合はチュートリアルをスキップ
    showTutorial.value = false
    console.log('登録済みユーザー、地図画面を表示')
  } else {
    console.log('新規ユーザー、チュートリアルを表示')
  }
  
  // デバッグモード確認
  await checkDebugMode()
  
  console.log('Vue版まちたんが起動しました！')
})
</script>

<style scoped>
#app {
  width: 100vw;
  height: 100vh;
}
</style>