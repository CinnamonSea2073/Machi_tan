<template>
  <div class="voice-button-container">
    <!-- 音量レベルメーター（録音中のみ表示） -->
    <div v-if="isRecording" class="level-container">
      <div class="level-meter" :style="{ background: levelBackground }"></div>
      <div v-if="showDebug" class="level-debug">{{ debugInfo }}</div>
    </div>
    
    <!-- 音声ボタン -->
    <button
      ref="voiceButton"
      class="voice-button"
      :class="{ recording: isRecording }"
      :disabled="isProcessing"
      @mousedown="handleMouseDown"
      @mouseup="handleMouseUp"
      @touchstart="handleTouchStart"
      @touchend="handleTouchEnd"
      @mouseleave="handleMouseLeave"
    >
      <span v-if="isProcessing">📤 送信中...</span>
      <span v-else-if="isRecording">🔴 録音中...離すと送信</span>
      <span v-else>🎤 長押しで報告</span>
    </button>

    <!-- 結果表示モーダル -->
    <div v-if="showModal" class="voice-modal" @click="closeModal">
      <div class="voice-modal-content" @click.stop>
        <div class="voice-result">
          <div v-if="result.transcript" class="transcript-section">
            <strong>あなたの報告:</strong>
            <p>{{ result.transcript }}</p>
          </div>
          <div v-if="result.response" class="response-section">
            <strong>隊長の返事:</strong>
            <p>{{ result.response }}</p>
          </div>
          <div v-if="errorMessage" class="error-section">
            <strong>エラー:</strong>
            <p>{{ errorMessage }}</p>
          </div>
        </div>
        <button @click="closeModal" class="close-button">閉じる</button>
      </div>
    </div>

    <!-- 再試行モーダル -->
    <div v-if="showRetryModal" class="voice-modal" @click="closeRetryModal">
      <div class="voice-modal-content" @click.stop>
        <div class="retry-content">
          <p><strong>音声が小さすぎます</strong></p>
          <p>もう一度大きな声で話してみてください。</p>
        </div>
        <div class="retry-buttons">
          <button @click="retryRecording" class="retry-button">もう一度録音</button>
          <button @click="closeRetryModal" class="cancel-button">キャンセル</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useVoiceRecording } from '../composables/useVoiceRecording.js'

const props = defineProps({
  showDebug: {
    type: Boolean,
    default: false
  }
})

// 音声録音機能
const {
  isRecording,
  isProcessing,
  levelPercent,
  debugInfo,
  startRecording,
  stopRecording,
  saveComment
} = useVoiceRecording()

// UI状態
const showModal = ref(false)
const showRetryModal = ref(false)
const result = ref({ transcript: '', response: '' })
const errorMessage = ref('')
const voiceButton = ref(null)

// レベルメーターの背景色計算
const levelBackground = computed(() => {
  const percent = levelPercent.value
  let color = '#7c4dff' // purple
  
  if (percent >= 60) color = '#4caf50' // green
  else if (percent >= 30) color = '#ffb300' // amber
  
  return `linear-gradient(90deg, ${color} ${percent}%, #eee ${percent}%)`
})

// マウス/タッチイベントハンドラ
const handleMouseDown = async (e) => {
  e.preventDefault()
  await startRecordingProcess()
}

const handleMouseUp = async (e) => {
  e.preventDefault()
  await stopRecordingProcess()
}

const handleTouchStart = async (e) => {
  e.preventDefault()
  await startRecordingProcess()
}

const handleTouchEnd = async (e) => {
  e.preventDefault()
  await stopRecordingProcess()
}

const handleMouseLeave = async (e) => {
  if (isRecording.value) {
    await stopRecordingProcess()
  }
}

// 録音開始処理
const startRecordingProcess = async () => {
  try {
    errorMessage.value = ''
    await startRecording()
  } catch (error) {
    console.error('Recording start error:', error)
    errorMessage.value = error.message
    showModal.value = true
  }
}

// 録音停止処理
const stopRecordingProcess = async () => {
  try {
    const recordingResult = await stopRecording()
    
    // 結果を表示
    result.value = recordingResult
    showModal.value = true
    
    // コメントとして保存
    try {
      await saveComment(recordingResult.transcript)
    } catch (err) {
      console.warn('Comment save failed:', err)
    }
    
  } catch (error) {
    console.error('Recording stop error:', error)
    
    if (error.message.includes('音声が検出されませんでした') || error.message.includes('小さすぎます')) {
      showRetryModal.value = true
    } else {
      errorMessage.value = error.message
      showModal.value = true
    }
  }
}

// モーダル制御
const closeModal = () => {
  showModal.value = false
  result.value = { transcript: '', response: '' }
  errorMessage.value = ''
}

const closeRetryModal = () => {
  showRetryModal.value = false
}

const retryRecording = () => {
  showRetryModal.value = false
  // ボタンにフォーカスを当てて再試行を促す
  nextTick(() => {
    if (voiceButton.value) {
      voiceButton.value.focus()
    }
  })
}
</script>

<style scoped>
.voice-button-container {
  position: relative;
}

.level-container {
  position: fixed;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.95);
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1001;
}

.level-meter {
  width: 200px;
  height: 8px;
  border-radius: 4px;
  margin-bottom: 4px;
}

.level-debug {
  font-size: 10px;
  color: #666;
  text-align: center;
}

.voice-button {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 32px;
  background: #1976d2;
  color: #fff;
  padding: 18px 28px;
  border-radius: 50px;
  border: none;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.4);
  cursor: pointer;
  user-select: none;
  touch-action: none;
  z-index: 1000;
  transition: all 0.2s;
  min-width: 200px;
  text-align: center;
}

.voice-button:active {
  background: #1565c0;
  transform: translateX(-50%) scale(0.95);
}

.voice-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: translateX(-50%);
}

.voice-button.recording {
  background: #d32f2f !important;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* モーダルスタイル */
.voice-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.voice-modal-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
}

.voice-result {
  margin-bottom: 20px;
}

.transcript-section,
.response-section,
.error-section {
  margin-bottom: 16px;
}

.transcript-section strong,
.response-section strong,
.error-section strong {
  display: block;
  margin-bottom: 8px;
  color: #333;
}

.transcript-section p {
  background: #e3f2fd;
  padding: 12px;
  border-radius: 8px;
  margin: 0;
}

.response-section p {
  background: #f3e5f5;
  padding: 12px;
  border-radius: 8px;
  margin: 0;
}

.error-section p {
  background: #ffebee;
  padding: 12px;
  border-radius: 8px;
  margin: 0;
  color: #c62828;
}

.close-button {
  width: 100%;
  padding: 12px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

.close-button:hover {
  background: #1565c0;
}

/* 再試行モーダル */
.retry-content {
  text-align: center;
  margin-bottom: 20px;
}

.retry-content p {
  margin: 8px 0;
}

.retry-buttons {
  display: flex;
  gap: 12px;
}

.retry-button,
.cancel-button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

.retry-button {
  background: #4caf50;
  color: white;
}

.retry-button:hover {
  background: #45a049;
}

.cancel-button {
  background: #f5f5f5;
  color: #333;
}

.cancel-button:hover {
  background: #e0e0e0;
}
</style>