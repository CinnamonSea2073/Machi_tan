<template>
  <div class="transceiver-container">
    <!-- 全画面処理中表示 -->
    <div v-if="isProcessing" class="fullscreen-processing-overlay">
      <div class="loading-spinner"></div>
      <div class="processing-text">処理中...</div>
    </div>
    
    <!-- トランシーバーUI -->
    <div 
      ref="transceiverElement"
      :class="['transceiver-ui', { 'visible': isVisible, 'recording': isRecording, 'disabled': disabled }]"
    >
      <!-- SVGトランシーバー -->
      <div class="transceiver-svg-container">
        <TransceiverSvg 
          :pressed="isPressed" 
          :width="432" 
          :height="864"
        />
      </div>
      
      <!-- 音声レベル表示 -->
      <div v-if="isRecording" class="voice-level-display">
        <div class="level-bars">
          <div 
            v-for="i in 8" 
            :key="i"
            :class="['level-bar', { active: currentLevel >= i }]"
            :style="{ 
              animationDelay: `${i * 0.1}s`,
              backgroundColor: currentLevel >= i ? getLevelColor(i) : '#333'
            }"
          ></div>
        </div>
        <div class="recording-text">音声認識中...</div>
      </div>
      
      <!-- デバッグ情報 -->
      <div v-if="debugMode" class="debug-info" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.8); color: white; padding: 5px; font-size: 12px; z-index: 1000;">
        Recording: {{ isRecording }}<br>
        Processing: {{ isProcessing }}<br>
        Pressed: {{ isPressed }}<br>
        Visible: {{ isVisible }}<br>
        HandlingPress: {{ isHandlingPress }}
      </div>
      
      <!-- 使用方法テキスト -->
      <div v-if="!isRecording && !isProcessing" class="instruction-text">
        {{ disabled ? '準備中...' : '長押しで音声入力' }}
      </div>
    </div>

    <!-- 音声応答結果モーダル -->
    <div v-if="showResponseModal" class="response-modal-overlay" @click.self="closeResponseModal">
      <div class="response-modal" @click.stop>
        <div class="modal-header">
          <h3>音声認識結果</h3>
          <button @click.stop.prevent="closeResponseModal" class="close-button">×</button>
        </div>
        <div class="modal-content">
          <div class="recognized-text">
            <strong>認識されたテキスト：</strong>
            <p>{{ recognizedText }}</p>
          </div>
          <div v-if="aiResponse" class="ai-response">
            <strong>AI応答：</strong>
            <p>{{ aiResponse }}</p>
          </div>
          <div class="modal-actions">
            <button @click.stop.prevent="closeResponseModal" class="modal-close-btn">
              閉じる
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import TransceiverSvg from './TransceiverSvg.vue'
import { useVoiceRecording } from '../composables/useVoiceRecording'

// Props
const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['hide', 'voice-result'])

// Voice recording composable
const { 
  isRecording, 
  isProcessing,
  currentLevel, 
  startRecording, 
  stopRecording,
  forceStop,
  lastRecognizedText,
  lastAiResponse 
} = useVoiceRecording()

// UI state  
const isVisible = ref(false) // 引き出された状態（false = 隠れた状態、true = 引き出された状態）
const isPressed = ref(false)
const showResponseModal = ref(false)
const recognizedText = ref('')
const aiResponse = ref('')
const transceiverElement = ref(null)

// デバッグモード状態
const debugMode = ref(false)

// Touch/mouse handling
let longPressTimer = null
const longPressDelay = 500 // 500ms
let isHandlingPress = false // 重複処理防止フラグ
let recordingStartPromise = null // 録音開始完了待ち
let forceStopTimer = null // 強制停止用タイマー

// クリーンアップ関数
const cleanup = () => {
  console.log('cleanup called')
  
  // 全てのタイマーをクリア  
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
  if (forceStopTimer) {
    clearTimeout(forceStopTimer)
    forceStopTimer = null
  }
  
  // 状態をリセット
  isPressed.value = false
  isHandlingPress = false
  
  // 録音を強制停止
  forceStop()
}

// イベントハンドラー関数
const handleTouchStart = (event) => {
  console.log('=== TOUCH START ===', { 
    type: event.type, 
    timeStamp: event.timeStamp,
    target: event.target.className,
    disabled: props.disabled
  })
  event.preventDefault()
  event.stopPropagation()
  
  // disabled状態では操作を無効化
  if (props.disabled) {
    console.log('トランシーバーが無効化されているため操作をスキップ')
    return
  }
  
  startLongPress()
}

const handleTouchEnd = (event) => {
  console.log('=== TOUCH END ===', { 
    type: event.type, 
    timeStamp: event.timeStamp,
    target: event.target.className,
    disabled: props.disabled
  })
  event.preventDefault()
  event.stopPropagation()
  
  // disabled状態では操作を無効化
  if (props.disabled) {
    console.log('トランシーバーが無効化されているため操作をスキップ')
    return
  }
  
  endLongPress()
}

const handleTouchMove = (event) => {
  console.log('=== TOUCH MOVE ===', { 
    type: event.type,
    isRecording: isRecording.value 
  })
  event.preventDefault()
  // タッチが移動した場合は長押しをキャンセル
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
    isPressed.value = false
  }
  // 録音中の場合は停止処理を実行
  if (isRecording.value) {
    console.log('Touch moved while recording, stopping')
    endLongPress()
  }
}

const handleMouseDown = (event) => {
  console.log('=== MOUSE DOWN ===', { 
    type: event.type, 
    button: event.button 
  })
  event.preventDefault()
  event.stopPropagation()
  startLongPress()
}

const handleMouseUp = (event) => {
  console.log('=== MOUSE UP ===', { 
    type: event.type, 
    button: event.button 
  })
  event.preventDefault()
  event.stopPropagation()
  endLongPress()
}

const handleMouseLeave = (event) => {
  console.log('=== MOUSE LEAVE ===', { 
    type: event.type 
  })
  endLongPress()
}

const startLongPress = () => {
  console.log('*** startLongPress called ***', {
    isVisible: isVisible.value,
    isHandlingPress,
    isRecording: isRecording.value,
    isPressed: isPressed.value
  })
  
  // 既に処理中の場合は無視
  if (isHandlingPress) {
    console.log('Already handling press, ignoring')
    return
  }
  
  // 隠れている状態の場合は引き出すのみ
  if (!isVisible.value) {
    console.log('Showing transceiver')
    isVisible.value = true
    return
  }
  
  // 長押し処理開始
  isHandlingPress = true
  isPressed.value = true
  console.log('Long press started, setting timer...')
  
  longPressTimer = setTimeout(() => {
    console.log('Long press timer fired, starting recording...')
    startRecording()
      .then(() => {
        console.log('Recording started successfully')
      })
      .catch((error) => {
        console.error('Recording start failed:', error)
        isPressed.value = false
        isHandlingPress = false
      })
  }, longPressDelay)
}

const endLongPress = () => {
  console.log('*** endLongPress called ***', {
    isRecording: isRecording.value,
    isPressed: isPressed.value,
    isHandlingPress,
    hasTimer: !!longPressTimer
  })
  
  // タイマーをクリア
  if (longPressTimer) {
    console.log('Clearing long press timer')
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
  
  // UI状態をリセット
  console.log('Resetting UI states')
  isPressed.value = false
  isHandlingPress = false
  
  // 録音中の場合のみ停止処理を実行
  if (isRecording.value) {
    console.log('Recording is active, stopping...')
    stopRecording()
      .then(result => {
        console.log('Recording stopped successfully, result:', result)
        if (result && (result.transcript || result.response)) {
          recognizedText.value = result.transcript || ''
          aiResponse.value = result.response || ''
          showResponseModal.value = true
        }
      })
      .catch(error => {
        console.error('Recording stop error:', error)
        forceStop()
        if (error.message !== 'No active recording to stop') {
          recognizedText.value = ''
          aiResponse.value = error.message || '音声認識に失敗しました'
          showResponseModal.value = true
        }
      })
  } else {
    console.log('No active recording to stop')
  }
  
  console.log('*** endLongPress completed ***')
}

// レベル表示色の計算
const getLevelColor = (level) => {
  if (level <= 2) return '#4CAF50' // 緑
  if (level <= 5) return '#FFC107' // 黄
  if (level <= 7) return '#FF9800' // オレンジ
  return '#F44336' // 赤
}

// モーダル関連
const closeResponseModal = () => {
  console.log('Closing response modal...', {
    showResponseModal: showResponseModal.value,
    recognizedText: recognizedText.value,
    aiResponse: aiResponse.value
  })
  
  // 音声結果をイベントとして発行（チュートリアル制御用）
  const voiceResult = {
    text: recognizedText.value,
    aiResponse: aiResponse.value,
    closed: true
  }
  emit('voice-result', voiceResult)
  
  showResponseModal.value = false
  recognizedText.value = ''
  aiResponse.value = ''
  
  // トランシーバーの状態もリセット
  isPressed.value = false
  
  console.log('Modal closed, showResponseModal:', showResponseModal.value)
}

// マップタップでトランシーバーを隠す
const handleMapTap = () => {
  if (isVisible.value && !isRecording.value) {
    hideTransceiver()
  }
}

const showTransceiver = () => {
  isVisible.value = true
}

const hideTransceiver = () => {
  isVisible.value = false
}

// ESCキーでトランシーバーを隠す、またはモーダルを閉じる
const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    if (showResponseModal.value) {
      // モーダルが開いている場合は閉じる
      closeResponseModal()
    } else if (isVisible.value && !isRecording.value) {
      // トランシーバーが表示中で録音中でない場合は隠す
      hideTransceiver()
    }
  }
}

// デバッグ用watcher
watch(showResponseModal, (newValue) => {
  console.log('showResponseModal changed:', newValue)
})

watch(isRecording, (newValue, oldValue) => {
  console.log('isRecording changed:', oldValue, '->', newValue)
})

watch(isPressed, (newValue, oldValue) => {
  console.log('isPressed changed:', oldValue, '->', newValue)
})

// デバッグモードチェック
const checkDebugMode = async () => {
  try {
    const res = await fetch('/api/status')
    if (!res.ok) return
    
    const data = await res.json()
    const currentStatus = data.status || ''
    debugMode.value = currentStatus === 'デバッグ'
  } catch (error) {
    console.warn('デバッグモードチェック失敗:', error)
  }
}

// 定期更新
let debugModeInterval = null

// Mount/unmount
onMounted(async () => {
  document.addEventListener('keydown', handleKeydown)
  
  // デバッグモードチェック（10秒間隔）
  await checkDebugMode()
  debugModeInterval = setInterval(checkDebugMode, 10000)
  
  // ネイティブイベントリスナーを設定
  const element = transceiverElement.value
  if (element) {
    console.log('Setting up native event listeners on element:', element)
    
    // タッチイベント
    element.addEventListener('touchstart', handleTouchStart, { passive: false })
    element.addEventListener('touchend', handleTouchEnd, { passive: false })
    element.addEventListener('touchmove', handleTouchMove, { passive: false })
    element.addEventListener('touchcancel', handleTouchEnd, { passive: false })
    
    // マウスイベント
    element.addEventListener('mousedown', handleMouseDown)
    element.addEventListener('mouseup', handleMouseUp)
    element.addEventListener('mouseleave', handleMouseLeave)
    
    console.log('Native event listeners set up successfully')
  } else {
    console.error('transceiverElement ref is null')
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  
  // ネイティブイベントリスナーを削除
  const element = transceiverElement.value
  if (element) {
    console.log('Removing native event listeners')
    
    // タッチイベント
    element.removeEventListener('touchstart', handleTouchStart)
    element.removeEventListener('touchend', handleTouchEnd)
    element.removeEventListener('touchmove', handleTouchMove)
    element.removeEventListener('touchcancel', handleTouchEnd)
    
    // マウスイベント
    element.removeEventListener('mousedown', handleMouseDown)
    element.removeEventListener('mouseup', handleMouseUp)
    element.removeEventListener('mouseleave', handleMouseLeave)
  }
  
  // インターバル停止
  if (debugModeInterval) {
    clearInterval(debugModeInterval)
  }
  
  // 完全なクリーンアップを実行
  cleanup()
})

watch(isVisible, (newValue) => {
  console.log('isVisible changed:', newValue)
})

defineExpose({
  showTransceiver,
  hideTransceiver,
  handleMapTap
})
</script>

<style scoped>
.transceiver-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  pointer-events: none;
}

.transceiver-ui {
  position: relative;
  width: 80vw;
  height: 64vh;
  max-height: 640px;
  margin: 0;
  margin-left: 0;
  padding: 32px 16px;
  border-radius: 0;
  transform: translateY(70%);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  pointer-events: auto;
  user-select: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.transceiver-ui.visible {
  transform: translateY(35%);
}

.transceiver-ui.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.transceiver-ui.disabled .instruction-text {
  color: #999;
}

.transceiver-svg-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  z-index: 1;
}

.transceiver-svg-container svg {
  display: block;
  margin: 0 auto;
}

.voice-level-display {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  padding: 0 40px;
  z-index: 2;
}

.level-bars {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 10px;
  height: 80px;
  margin-bottom: 20px;
  max-width: 320px;
  margin-left: auto;
  margin-right: auto;
}

.level-bar {
  width: 16px;
  height: 100%;
  border-radius: 8px;
  background: #333;
  transition: all 0.2s ease;
  transform-origin: bottom;
}

.level-bar.active {
  animation: pulse 0.6s infinite alternate;
}

@keyframes pulse {
  0% { transform: scaleY(0.3); opacity: 0.7; }
  100% { transform: scaleY(1); opacity: 1; }
}

.recording-text {
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  text-shadow: 0 3px 6px rgba(0, 0, 0, 0.8);
}

.fullscreen-processing-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  z-index: 9999;
  text-align: center;
  padding: 0 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(157, 87, 255, 0.3);
  border-top: 4px solid #9D57FF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.processing-text {
  color: #9D57FF;
  font-size: 20px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
}

.instruction-text {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  color: #ccc;
  font-size: 19px;
  font-weight: 600;
  padding: 0 32px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
  z-index: 2;
}

/* レスポンシブモーダル */
.response-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(5px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.response-modal {
  background: linear-gradient(145deg, #2a2a2a 0%, #1a1a1a 100%);
  border-radius: 15px;
  padding: 20px;
  margin: 20px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  color: #fff;
  margin: 0;
  font-size: 18px;
}

.close-button {
  background: none;
  border: none;
  color: #ccc;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  min-width: 40px;
  min-height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  pointer-events: auto;
  z-index: 2001;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.modal-content {
  color: #fff;
}

.recognized-text,
.ai-response {
  margin-bottom: 20px;
}

.recognized-text strong,
.ai-response strong {
  color: #9D57FF;
  display: block;
  margin-bottom: 8px;
}

.recognized-text p,
.ai-response p {
  margin: 0;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border-left: 3px solid #9D57FF;
  line-height: 1.5;
}

.modal-actions {
  margin-top: 20px;
  text-align: center;
}

.modal-close-btn {
  background: linear-gradient(145deg, #9D57FF 0%, #7C3AED 100%);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s ease;
  pointer-events: auto;
}

.modal-close-btn:hover {
  background: linear-gradient(145deg, #7C3AED 0%, #6D28D9 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(157, 87, 255, 0.3);
}

/* タッチデバイス対応 */
@media (max-width: 768px) {
  .transceiver-ui {
    width: 85vw;
    height: 56vh;
    max-height: 480px;
    margin: 0;
    margin-left: 2.5vw;
    padding: 24px 12px;
  }
  
  .transceiver-svg-container svg {
    width: 320px;
    height: 640px;
  }
  
  .level-bars {
    height: 64px;
    gap: 6px;
    max-width: 240px;
  }
  
  .level-bar {
    width: 13px;
    border-radius: 6px;
  }
  
  .recording-text {
    font-size: 19px;
  }
  
  .processing-text {
    font-size: 18px;
  }
  
  .loading-spinner {
    width: 32px;
    height: 32px;
    border-width: 3px;
  }
  
  .instruction-text {
    font-size: 16px;
  }
  
  .response-modal {
    margin: 10px;
    padding: 15px;
  }
  
  .modal-header h3 {
    font-size: 16px;
  }
}
</style>