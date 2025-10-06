<template>
  <div class="loading-screen">
    <div class="loading-container">
      <!-- Lottieキャラクター -->
      <div ref="lottieContainer" class="lottie-container"></div>
      
      <!-- オプションのメッセージ -->
      <div v-if="message" class="loading-message">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import lottie from 'lottie-web'

// Props
const props = defineProps({
  message: {
    type: String,
    default: ''
  }
})

// Template ref
const lottieContainer = ref(null)

// Lottie animation instance
let animationInstance = null

// Lottieアニメーションを初期化
const initLottie = async () => {
  if (!lottieContainer.value) return
  
  try {
    // 既存のアニメーションがあれば削除
    if (animationInstance) {
      animationInstance.destroy()
      animationInstance = null
    }
    
    // Lottieアニメーションを読み込み
    animationInstance = lottie.loadAnimation({
      container: lottieContainer.value,
      renderer: 'svg',
      loop: true,
      autoplay: true,
      // 指定されたLottie URLから読み込み
      path: 'https://lottie.host/5a0d339e-c731-45a9-8fa9-7dcd81f67d76/84g6NBGOge.json'
    })
    
    console.log('Lottie animation loaded successfully')
  } catch (error) {
    console.error('Lottie animation failed to load:', error)
  }
}

// クリーンアップ
const cleanup = () => {
  if (animationInstance) {
    animationInstance.destroy()
    animationInstance = null
  }
}

// マウント時に初期化
onMounted(() => {
  // 少し遅延させてDOMが確実に準備されるのを待つ
  setTimeout(initLottie, 100)
})

// アンマウント時にクリーンアップ
onUnmounted(() => {
  cleanup()
})

// メッセージが変更された場合の処理（必要に応じて）
watch(() => props.message, (newMessage) => {
  console.log('Loading message changed:', newMessage)
})
</script>

<style scoped>
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 400px;
  padding: 20px;
}

.lottie-container {
  width: 300px;
  height: 300px;
  max-width: 80vw;
  max-height: 40vh;
}

.loading-message {
  margin-top: 20px;
  font-size: 18px;
  color: #333;
  text-align: center;
  font-weight: 500;
  line-height: 1.5;
}

/* レスポンシブ対応 */
@media (max-width: 480px) {
  .lottie-container {
    width: 250px;
    height: 250px;
  }
  
  .loading-message {
    font-size: 16px;
    margin-top: 16px;
  }
}

@media (max-height: 600px) {
  .lottie-container {
    width: 200px;
    height: 200px;
  }
  
  .loading-message {
    font-size: 14px;
    margin-top: 12px;
  }
}
</style>