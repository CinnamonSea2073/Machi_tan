import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

export function useStatusControl() {
  // 状態管理
  const currentStatus = ref('')
  const isLoading = ref(true)
  const lastStatus = ref('')
  
  // ステータス監視用インターバル
  let statusInterval = null
  
  // 計算プロパティ（バックエンドAPIの正しいステータス値に対応）
  const isPreparation = computed(() => currentStatus.value === 'チュートリアル')
  const isInProgress = computed(() => currentStatus.value === '実行中')
  const isCompleted = computed(() => currentStatus.value === '結果')
  const isBreak = computed(() => currentStatus.value === '終了') // 休憩・終了として扱う
  const isDebug = computed(() => currentStatus.value === 'デバッグ')
  
  // ステータスが変更されたかを判定
  const statusChanged = computed(() => {
    return lastStatus.value !== '' && lastStatus.value !== currentStatus.value
  })
  
  // ステータス取得
  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status')
      if (!res.ok) {
        console.warn('ステータス取得失敗:', res.status)
        return
      }
      
      const data = await res.json()
      const newStatus = data.status || ''
      
      // ステータス変更を検出
      if (currentStatus.value !== newStatus) {
        lastStatus.value = currentStatus.value
        currentStatus.value = newStatus
        console.log('ステータス変更:', lastStatus.value, '->', currentStatus.value)
      }
      
      isLoading.value = false
    } catch (error) {
      console.warn('ステータス取得エラー:', error)
    }
  }
  
  // 初期化
  const initialize = async () => {
    await fetchStatus()
    
    // 5秒間隔でステータスをポーリング
    statusInterval = setInterval(fetchStatus, 5000)
  }
  
  // クリーンアップ
  const cleanup = () => {
    if (statusInterval) {
      clearInterval(statusInterval)
      statusInterval = null
    }
  }
  
  // 現在のユーザー状態を判定
  const shouldShowTutorial = computed(() => {
    // 「チュートリアル」ステータスの場合はチュートリアルを表示
    return isPreparation.value
  })
  
  const shouldShowLoading = computed(() => {
    // 初期ロード中、「終了」ステータス時（休憩・待機）、またはチュートリアル完了後の待機状態で表示
    return isLoading.value || isBreak.value
  })
  
  const shouldShowMap = computed(() => {
    // 「実行中」または「デバッグ」ステータスの場合はマップを表示
    return isInProgress.value || isDebug.value
  })
  
  const shouldShowResult = computed(() => {
    // 「結果」ステータスの場合はリザルト画面を表示
    return isCompleted.value
  })
  
  // 学生がチュートリアルを完了したかを追跡
  const tutorialCompleted = ref(false)
  
  const completeTutorial = () => {
    tutorialCompleted.value = true
    console.log('チュートリアル完了')
  }
  
  // チュートリアル完了後で実行中以外の場合はローディング表示
  const shouldShowPostTutorialLoading = computed(() => {
    return tutorialCompleted.value && !shouldShowMap.value && !shouldShowResult.value
  })
  
  // ステータス変更を監視してチュートリアル状態をリセット
  watch(currentStatus, (newStatus, oldStatus) => {
    // ステータスが「チュートリアル」に変更された場合、チュートリアル完了状態をリセット
    if (newStatus === 'チュートリアル' && oldStatus !== 'チュートリアル') {
      tutorialCompleted.value = false
      console.log('ステータスが「チュートリアル」に変更されたため、チュートリアル完了状態をリセットしました')
    }
  })

  // マウント時に初期化
  onMounted(() => {
    initialize()
  })
  
  // アンマウント時にクリーンアップ
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    // 状態
    currentStatus,
    isLoading,
    lastStatus,
    tutorialCompleted,
    
    // 計算プロパティ
    isPreparation,
    isInProgress,
    isCompleted,
    isBreak,
    isDebug,
    statusChanged,
    shouldShowTutorial,
    shouldShowLoading,
    shouldShowMap,
    shouldShowResult,
    shouldShowPostTutorialLoading,
    
    // メソッド
    fetchStatus,
    completeTutorial,
    cleanup
  }
}