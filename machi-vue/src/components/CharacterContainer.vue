<template>
  <div 
    ref="characterContainer" 
    class="character-container"
    :class="{ loading: isLoading }"
  >
    <!-- Lottie読み込み中の表示 -->
    <div v-if="isLoading" class="loading-placeholder">
      <div class="loading-text">た</div>
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useLottieAnimations } from '../composables/useLottieAnimations.js'

const props = defineProps({
  animationUrl: {
    type: String,
    required: true
  }
})

const characterContainer = ref(null)
const { switchToCharacter, playAnimation, isLoading } = useLottieAnimations()

// アニメーションURLが変更されたときにキャラクターを切り替え
watch(() => props.animationUrl, (newUrl) => {
  if (newUrl && characterContainer.value && !isLoading.value) {
    switchToCharacter(newUrl, characterContainer.value)
  }
}, { immediate: true })

// ローディング完了後に初期アニメーションを設定
watch(isLoading, (loading) => {
  if (!loading && props.animationUrl && characterContainer.value) {
    switchToCharacter(props.animationUrl, characterContainer.value)
  }
})

// 外部からアニメーション再生をトリガー可能
defineExpose({
  playAnimation
})

onMounted(() => {
  // コンテナの準備ができたら初期化
  if (props.animationUrl && characterContainer.value && !isLoading.value) {
    switchToCharacter(props.animationUrl, characterContainer.value)
  }
})
</script>

<style scoped>
.character-container {
  width: 210px;
  height: 210px;
  border-radius: 16px;
  background: #d9d9d9;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.character-container.loading {
  background: #f8f9fa;
}

.loading-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.loading-text {
  font-size: 48px;
  color: #666;
  margin-bottom: 10px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e0e0e0;
  border-top: 2px solid #666;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Lottieアニメーションのスタイル調整 */
.character-container :deep(svg) {
  width: 100%;
  height: 100%;
}
</style>