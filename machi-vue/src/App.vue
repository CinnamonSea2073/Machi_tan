<template>
  <div id="app">
    <!-- 先生用ページ -->
    <TeacherScreen v-if="isTeacherMode" />
    
    <!-- 学生用ページ -->
    <template v-else>
      <!-- ステータス制御による画面切り替え -->
      
      <!-- チュートリアル画面 -->
      <TutorialScreen 
        v-if="currentStatus === 'チュートリアル' && !tutorialCompleted" 
        @complete="handleTutorialComplete"
      />
      
      <!-- リザルト画面（完了時） -->
      <ResultScreen 
        v-else-if="shouldShowResult"
        :student-name="studentName"
      />
      
      <!-- マップ画面（実行中、デバッグ時） -->
      <MapScreen 
        v-else-if="shouldShowMap"
      />
      
      <!-- ローディング画面（その他すべての場合） -->
      <LoadingScreen 
        v-else
        :message="loadingMessage"
      />
      
      <!-- デバッグパネル（デバッグモード時のみ） -->
      <DebugPanel 
        v-if="isDebug && !isTeacherMode" 
        @show-tutorial="forceShowTutorial"
        @show-map="forceShowMap" 
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import TutorialScreen from './components/TutorialScreen.vue'
import MapScreen from './components/MapScreen.vue'
import TeacherScreen from './components/TeacherScreen.vue'
import DebugPanel from './components/DebugPanel.vue'
import LoadingScreen from './components/LoadingScreen.vue'
import ResultScreen from './components/ResultScreen.vue'
import { useStatusControl } from './composables/useStatusControl.js'

// ページモード判定
const isTeacherMode = computed(() => {
  const urlParams = new URLSearchParams(window.location.search)
  return urlParams.get('mode') === 'teacher'
})

// ステータス制御システム
const {
  currentStatus,
  isLoading,
  tutorialCompleted,
  shouldShowTutorial,
  shouldShowLoading,
  shouldShowMap,
  shouldShowResult,
  shouldShowPostTutorialLoading,
  isDebug,
  completeTutorial
} = useStatusControl()

// 学生名
const studentName = ref('')

// ローディング画面のメッセージ
const loadingMessage = computed(() => {
  console.log('ローディングメッセージ計算:', {
    isLoading: isLoading.value,
    shouldShowPostTutorialLoading: shouldShowPostTutorialLoading.value,
    currentStatus: currentStatus.value,
    tutorialCompleted: tutorialCompleted.value
  })
  
  if (isLoading.value) {
    return 'システムを準備中...'
  } else if (tutorialCompleted.value && currentStatus.value !== '実行中' && currentStatus.value !== '結果') {
    return 'みんなの準備が整うまでお待ちください...'
  } else if (currentStatus.value === '終了') {
    return '休憩中です。先生の指示をお待ちください...'
  } else {
    return 'お待ちください...'
  }
})

// チュートリアル完了ハンドラー
const handleTutorialComplete = () => {
  completeTutorial()
  console.log('チュートリアル完了、待機状態に移行します')
}

// デバッグパネル用の強制表示関数
const forceShowTutorial = () => {
  // デバッグ用：強制的にチュートリアルを表示
  tutorialCompleted.value = false
  localStorage.removeItem('studentUuid')
  localStorage.removeItem('studentName')
}

const forceShowMap = () => {
  // デバッグ用：強制的にマップを表示（通常は使用しない）
  console.log('デバッグ：マップ画面を強制表示')
}

onMounted(async () => {
  // 学生名を取得
  studentName.value = localStorage.getItem('studentName') || '匿名ユーザー'
  
  // 既存のチュートリアル完了状態をチェック
  if (localStorage.getItem('studentUuid')) {
    tutorialCompleted.value = true
    console.log('登録済みユーザー、ステータスに応じて画面表示')
  } else {
    console.log('新規ユーザー、ステータスに応じてチュートリアル表示')
  }
  
  console.log('Vue版まちたんが起動しました（ステータス制御対応）！')
})

// ステータス変更を監視してログ出力とチュートリアル状態管理
watch(currentStatus, (newStatus, oldStatus) => {
  console.log(`ステータス変更: ${oldStatus} → ${newStatus}`)
  
  // ステータスが「チュートリアル」に変更された場合の処理
  if (newStatus === 'チュートリアル') {
    console.log('チュートリアルステータスが設定されました。チュートリアルを開始します。')
  }
})
</script>

<style scoped>
#app {
  width: 100vw;
  height: 100vh;
}
</style>