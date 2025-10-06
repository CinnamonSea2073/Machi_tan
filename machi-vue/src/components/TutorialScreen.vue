<template>
  <div class="tutorial-screen" @click="handleScreenClick">
    <!-- マップステップ表示 -->
    <div v-if="isMapStep" class="map-tutorial-container">
      <!-- マップコンテナ -->
      <div id="tutorial-map" ref="tutorialMapContainer" class="tutorial-map"></div>
      
      <!-- 吹き出し（マップ上にオーバーレイ） -->
      <div class="map-tutorial-bubble-overlay">
        <TutorialBubble v-if="displayMessage" :message="displayMessage" />
      </div>
      
      <!-- ヒントテキスト（マップ上にオーバーレイ） -->
      <div class="map-tutorial-hint">
        どこでもタップで次へ
      </div>
    </div>
    
    <!-- 通常のチュートリアル表示 -->
    <div v-else class="tutorial-container">
      <!-- メッセージ吹き出し -->
      <div class="tutorial-bubble-section">
        <TutorialBubble v-if="displayMessage" :message="displayMessage" />
      </div>
      
      <!-- キャラクター -->
      <div class="character-section">
        <CharacterContainer 
          ref="characterContainer"
          :animationUrl="currentCharacterUrl" 
        />
      </div>
      
      <!-- 名前入力フォーム（Step9で表示） -->
      <div v-if="isNameInputStep" class="name-input-section">
        <NameInputForm @submit="handleNameSubmit" />
      </div>
      
      <!-- ヒントテキスト -->
      <div v-if="!isNameInputStep && !shouldShowTransceiver" class="tutorial-hint">
        どこでもタップで次へ
      </div>
      
      <!-- Step8でのヒントテキスト -->
      <div v-if="shouldShowTransceiver && isVoiceInputRequired" class="tutorial-hint voice-hint">
        トランシーバーのボタンを押しながら話してください
      </div>
    </div>
    
    <!-- トランシーバーボタン（Step6-8で表示） -->
    <TransceiverButton 
      v-if="shouldShowTransceiver"
      ref="transceiverButton"
      :disabled="!isTransceiverInteractive"
      @voice-result="handleVoiceResult"
      @hide="hideTransceiver"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import L from 'leaflet'
import CharacterContainer from './CharacterContainer.vue'
import TutorialBubble from './TutorialBubble.vue'
import NameInputForm from './NameInputForm.vue'
import TransceiverButton from './TransceiverButton.vue'
import { useTutorial, tutorialStory } from '../composables/useTutorial.js'

// 親コンポーネントとの通信
const emit = defineEmits(['complete'])

// チュートリアル機能の初期化
const {
  currentStep,
  totalSteps,
  currentStepData,
  isCompleted,
  nextStep: tutorialNextStep,
  previousStep,
  setNameAndNext,
  getDisplayMessage
} = useTutorial()

// テンプレート参照
const characterContainer = ref(null)
const transceiverButton = ref(null)
const tutorialMapContainer = ref(null)

// チュートリアル状態管理
const hasCompletedVoiceInput = ref(false)

// マップ関連の状態
const tutorialMap = ref(null)
const userPositionMarker = ref(null)
const dummyStarMarker = ref(null)

// 計算されたプロパティ
const progressPercent = computed(() => (currentStep.value / (totalSteps.value || tutorialStory.length)) * 100)
const isLastStep = computed(() => currentStep.value === (totalSteps.value || tutorialStory.length))
const isNameInputStep = computed(() => {
  const step = currentStepData.value
  return step && step.isNameInput === true
})
const isWaitingForName = computed(() => {
  const step = currentStepData.value
  return step && step.isNameDisplay && !localStorage.getItem('studentName')
})

// トランシーバー表示制御
const shouldShowTransceiver = computed(() => {
  const step = currentStepData.value
  return step && step.showTransceiver === true
})

// トランシーバー操作可否
const isTransceiverInteractive = computed(() => {
  const step = currentStepData.value
  return step && step.transceiverInteractive === true
})

// 音声入力必須ステップかどうか
const isVoiceInputRequired = computed(() => {
  const step = currentStepData.value
  return step && step.requireVoiceInput === true
})

// マップステップかどうか
const isMapStep = computed(() => {
  const step = currentStepData.value
  return step && step.isMapStep === true
})

// 現在のキャラクターURL
const currentCharacterUrl = computed(() => {
  const step = currentStepData.value
  if (!step || !step.character) {
    // デフォルトキャラクター
    return 'https://lottie.host/f388a0b2-cce4-4681-a943-d8fb67a984d7/XfkX4AvJZo.json'
  }
  
  // tutorialStoryのcharacterフィールドは直接URLを格納
  return step.character
})

// 表示メッセージ
const displayMessage = computed(() => {
  try {
    return getDisplayMessage() || ''
  } catch (error) {
    console.error('Display message error:', error)
    return ''
  }
})

// 画面クリックで進行
let isProcessingClick = false
const handleScreenClick = async () => {
  if (isProcessingClick) {
    console.log('クリック処理中のため無視')
    return
  }
  
  isProcessingClick = true
  console.log('=== 画面クリック検出 ===')
  console.log(`名前入力ステップ?: ${isNameInputStep.value}`)
  console.log(`音声入力必須ステップ?: ${isVoiceInputRequired.value}`)
  console.log(`音声入力完了済み?: ${hasCompletedVoiceInput.value}`)
  console.log(`現在のステップ: ${currentStep.value}`)
  console.log(`現在のステップデータ:`, currentStepData.value)
  
  try {
    // Step9（isNameInput: true）の時はクリック無効
    if (isNameInputStep.value) {
      console.log('名前入力中のためクリック無効')
      return
    }
    
    // Step8（音声入力必須）の時は音声入力完了まで進行不可
    if (isVoiceInputRequired.value && !hasCompletedVoiceInput.value) {
      console.log('音声入力未完了のためクリック無効')
      return
    }
    
    console.log('nextStep()を実行')
    await nextStep()
  } finally {
    isProcessingClick = false
  }
}

// ステップ制御
const nextStep = async () => {
  const totalStepsValue = totalSteps.value || tutorialStory.length // バックアップ値
  console.log(`Step ${currentStep.value} → 次のステップ (総ステップ数: ${totalStepsValue})`)
  console.log(`現在のステップデータ:`, currentStepData.value)
  console.log(`Step10判定: ${currentStep.value} === ${totalStepsValue} = ${currentStep.value === totalStepsValue}`)
  
  // Step10で画面をクリックした場合の完了処理
  if (currentStep.value === totalStepsValue) {
    console.log('Step10完了 → チュートリアル終了')
    await handleTutorialComplete()
    return
  }
  
  console.log('通常のステップ進行処理')
  
  // 次のステップに移る前に音声入力完了フラグをリセット
  hasCompletedVoiceInput.value = false
  
  tutorialNextStep()
  console.log(`進行後 - 現在のステップ: ${currentStep.value}, 完了状態: ${isCompleted.value}`)
  
  // キャラクターアニメーションをトリガー
  await nextTick()
  if (characterContainer.value) {
    characterContainer.value.playAnimation?.()
  }
}

// 名前入力の処理
const handleNameSubmit = async (name) => {
  try {
    // APIに学生を登録（元のエンドポイントに合わせて修正）
    const response = await fetch('/api/students', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: name
      })
    })
    
    if (!response.ok) {
      throw new Error('学生登録に失敗しました')
    }
    
    const result = await response.json()
    
    // UUIDを保存（元のレスポンス形式に合わせて修正）
    localStorage.setItem('studentUuid', result.student_id)
    console.log('学生登録完了:', result)
    
    // 名前を設定して次のステップへ
    setNameAndNext(name)
    console.log(`名前登録後のステップ: ${currentStep.value}`)
    
    // キャラクターアニメーションをトリガー
    await nextTick()
    if (characterContainer.value) {
      characterContainer.value.playAnimation?.()
    }
    
  } catch (error) {
    console.error('学生登録エラー:', error)
    // エラー時も進行を続ける（オフライン対応）
    setNameAndNext(name)
    console.log(`エラー後のステップ: ${currentStep.value}`)
  }
}

// 音声入力結果処理
const handleVoiceResult = async (result) => {
  console.log('音声入力結果を受信:', result)
  
  if (isVoiceInputRequired.value) {
    // Step8での音声入力完了
    hasCompletedVoiceInput.value = true
    console.log('音声入力完了フラグを設定')
    
    // 結果が閉じられたら自動的に次のステップに進む
    if (result.closed) {
      console.log('音声結果が閉じられました。次のステップに進行します。')
      await nextStep()
    }
  }
}

// トランシーバーを隠す
const hideTransceiver = () => {
  // TransceiverButton内で管理するため、特別な処理は不要
  console.log('トランシーバーが隠されました')
}

// マップ初期化
const initTutorialMap = () => {
  if (!tutorialMapContainer.value || tutorialMap.value) return
  
  console.log('チュートリアル用マップを初期化中...')
  
  // 柏の葉周辺の座標（例：TX柏の葉キャンパス駅周辺）
  const kashiwanohaCenter = [35.8918, 139.9441]
  
  tutorialMap.value = L.map(tutorialMapContainer.value, {
    zoomControl: false,
    attributionControl: true,
    dragging: false, // ドラッグ無効
    touchZoom: false, // タッチズーム無効
    doubleClickZoom: false, // ダブルクリックズーム無効
    scrollWheelZoom: false, // スクロールズーム無効
    boxZoom: false, // ボックスズーム無効
    keyboard: false // キーボード操作無効
  }).setView(kashiwanohaCenter, 15)
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(tutorialMap.value)
  
  console.log('チュートリアル用マップが初期化されました')
}

// マップフォーカス制御
const updateMapFocus = async () => {
  if (!tutorialMap.value || !isMapStep.value) return
  
  const step = currentStepData.value
  const focusType = step.mapFocus
  
  console.log('マップフォーカス更新:', focusType)
  
  // 既存のマーカーをクリア
  if (userPositionMarker.value) {
    tutorialMap.value.removeLayer(userPositionMarker.value)
    userPositionMarker.value = null
  }
  if (dummyStarMarker.value) {
    tutorialMap.value.removeLayer(dummyStarMarker.value)
    dummyStarMarker.value = null
  }
  
  const kashiwanohaCenter = [35.8918, 139.9441]
  
  switch (focusType) {
    case 'user-position':
      // ユーザー位置マーカーを表示（水色の円）
      userPositionMarker.value = L.circleMarker(kashiwanohaCenter, {
        radius: 15,
        fillColor: '#00BFFF',
        color: '#0080FF',
        weight: 3,
        opacity: 1,
        fillOpacity: 0.6
      }).addTo(tutorialMap.value)
      
      tutorialMap.value.setView(kashiwanohaCenter, 16)
      break
      
    case 'star':
      // ユーザー位置マーカーも表示
      userPositionMarker.value = L.circleMarker(kashiwanohaCenter, {
        radius: 15,
        fillColor: '#00BFFF',
        color: '#0080FF',
        weight: 3,
        opacity: 1,
        fillOpacity: 0.6
      }).addTo(tutorialMap.value)
      
      // 中央付近にダミーの星を表示（より目立つ位置）
      const starPosition = [35.8920, 139.9445] // ユーザー位置から少し北に配置
      const starIcon = L.divIcon({
        className: 'tutorial-star-marker',
        html: `
          <div class="star-marker-container">
            <div class="star-pulse"></div>
            <div class="star-icon">⭐</div>
          </div>
        `,
        iconSize: [60, 60],
        iconAnchor: [30, 30]
      })
      dummyStarMarker.value = L.marker(starPosition, { 
        icon: starIcon,
        zIndexOffset: 1000
      }).addTo(tutorialMap.value)
      
      // 星を中央に表示してズームレベルを調整
      tutorialMap.value.setView(starPosition, 18)
      
      console.log('星マーカー表示:', starPosition)
      break
      
    case 'overview':
      // ユーザー位置と星の両方を表示
      userPositionMarker.value = L.circleMarker(kashiwanohaCenter, {
        radius: 15,
        fillColor: '#00BFFF',
        color: '#0080FF',
        weight: 3,
        opacity: 1,
        fillOpacity: 0.6
      }).addTo(tutorialMap.value)
      
      // 同じ星の座標を使用（一貫性のため）
      const overviewStarPosition = [35.8920, 139.9445]
      const overviewStarIcon = L.divIcon({
        className: 'tutorial-star-marker',
        html: `
          <div class="star-marker-container">
            <div class="star-icon">⭐</div>
          </div>
        `,
        iconSize: [40, 40],
        iconAnchor: [20, 20]
      })
      dummyStarMarker.value = L.marker(overviewStarPosition, { 
        icon: overviewStarIcon,
        zIndexOffset: 1000
      }).addTo(tutorialMap.value)
      
      // 両方が見えるようにズーム調整（中心点を調整）
      const centerPoint = [
        (kashiwanohaCenter[0] + overviewStarPosition[0]) / 2,
        (kashiwanohaCenter[1] + overviewStarPosition[1]) / 2
      ]
      tutorialMap.value.setView(centerPoint, 16)
      
      console.log('概要マップ表示:', centerPoint)
      break
  }
}

// チュートリアル完了処理
let isCompleting = false
const handleTutorialComplete = async () => {
  if (isCompleting) {
    console.log('チュートリアル完了処理は既に実行中です')
    return
  }
  
  isCompleting = true
  console.log('チュートリアル完了処理を開始')
  
  try {
    // 完了をlocalStorageに記録
    localStorage.setItem('tutorialCompleted', 'true')
    localStorage.setItem('tutorialCompletedAt', new Date().toISOString())
    
    console.log('チュートリアル完了、待機画面に遷移します')
    // 親コンポーネントに完了を通知
    emit('complete')
    
  } catch (error) {
    console.error('チュートリアル完了処理エラー:', error)
    // エラーでも進行
    emit('complete')
  } finally {
    isCompleting = false
  }
}

// ステップ変更時のマップ更新
watch([currentStep, isMapStep], async () => {
  if (isMapStep.value) {
    await nextTick()
    initTutorialMap()
    await updateMapFocus()
  }
}, { immediate: true })

// 初期化
onMounted(() => {
  console.log('チュートリアル開始')
  console.log('TutorialScreen - totalSteps:', totalSteps.value)
  console.log('TutorialScreen - currentStep:', currentStep.value)
})

// クリーンアップ
onUnmounted(() => {
  if (tutorialMap.value) {
    tutorialMap.value.remove()
    tutorialMap.value = null
  }
})
</script>

<style scoped>
.tutorial-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #ffffff;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #111;
  font-family: sans-serif;
  padding: 24px;
  box-sizing: border-box;
  cursor: pointer;
}

.tutorial-container {
  width: 360px;
  max-width: 94vw;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.tutorial-bubble-section {
  order: 1;
}

.character-section {
  order: 2;
}

.name-input-section {
  order: 3;
  width: 100%;
  cursor: default;
}

.name-input-section * {
  cursor: default;
}

.tutorial-hint {
  order: 4;
  font-size: 13px;
  opacity: 0.9;
  text-align: center;
  color: rgba(0, 0, 0, 0.7);
}

.voice-hint {
  color: #9D57FF;
  font-weight: 500;
  font-size: 14px;
}

/* マップステップ用スタイル */
.map-tutorial-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #ffffff;
  z-index: 9999;
}

.tutorial-map {
  width: 100%;
  height: 100%;
}

.map-tutorial-bubble-overlay {
  position: absolute;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  pointer-events: none;
}

.map-tutorial-hint {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  font-size: 13px;
  opacity: 0.9;
  text-align: center;
  color: rgba(0, 0, 0, 0.7);
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  pointer-events: none;
}

/* 星マーカー用スタイル */
:global(.tutorial-star-marker) {
  z-index: 1000 !important;
}

:global(.star-marker-container) {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

:global(.star-icon) {
  font-size: 32px;
  color: #FFD700;
  text-shadow: 
    0 0 6px rgba(255, 215, 0, 0.8),
    0 0 12px rgba(255, 255, 255, 0.6),
    2px 2px 4px rgba(0, 0, 0, 0.3);
  animation: starPulse 2s ease-in-out infinite;
  position: relative;
  z-index: 1001;
  transform-origin: center;
}

:global(.star-icon::before) {
  content: '';
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  background: radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  animation: starGlow 2s ease-in-out infinite;
  z-index: -1;
}

@keyframes starPulse {
  0%, 100% { 
    transform: scale(1);
  }
  50% { 
    transform: scale(1.3);
  }
}

@keyframes starGlow {
  0%, 100% { 
    opacity: 0.5;
    transform: scale(1);
  }
  50% { 
    opacity: 1;
    transform: scale(1.5);
  }
}
</style>