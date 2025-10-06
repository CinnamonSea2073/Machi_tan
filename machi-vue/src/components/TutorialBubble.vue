<template>
  <div class="tutorial-bubble" :class="{ 'bubble-animate': animate }">
    <div class="bubble-svg">
      <svg width="315" height="121" viewBox="0 0 315 121" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g>
          <path d="M304.075 0H10.9249C4.89123 0 4.34115e-06 4.87327 4.34115e-06 10.8848L0 78.461C0 84.4724 4.89123 89.3457 10.9249 89.3457H119.945C123.132 89.3457 126.189 90.6139 128.44 92.8706L148.72 113.199C153.518 118.009 161.348 117.88 165.985 112.915L184.441 93.1548C186.71 90.7251 189.886 89.3457 193.211 89.3457H304.075C310.109 89.3457 315 84.4724 315 78.461V10.8848C315 4.87327 310.109 0 304.075 0Z" fill="white"/>
          <path d="M10.9248 1H304.075C309.56 1.00003 314 5.42905 314 10.8848V78.4609C314 83.9167 309.56 88.3457 304.075 88.3457H193.211C189.609 88.3457 186.168 89.8404 183.71 92.4727L165.255 112.232C161.004 116.784 153.826 116.902 149.428 112.493L129.148 92.1641C126.71 89.7195 123.398 88.3458 119.945 88.3457H10.9248C5.44001 88.3457 1 83.9167 1 78.4609V10.8848C1 5.59944 5.167 1.27752 10.4141 1.0127L10.9248 1Z" stroke="#929292" stroke-width="2"/>
        </g>
      </svg>
    </div>
    <div class="bubble-content">
      <div class="bubble-text" v-html="displayMessage"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, ref } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true
  },
  animate: {
    type: Boolean,
    default: false
  }
})

// 改行文字を<br>に変換
const displayMessage = computed(() => {
  return props.message.replace(/\n/g, '<br>')
})

// アニメーション制御
const animate = ref(false)

watch(() => props.message, () => {
  // メッセージが変わったときにアニメーションをトリガー
  animate.value = true
  setTimeout(() => {
    animate.value = false
  }, 600)
})
</script>

<style scoped>
/* 既存のCSSを移植 */
.tutorial-bubble {
  background: transparent;
  color: #111;
  border-radius: 14px;
  padding: 0;
  max-width: 94vw;
  position: relative;
  box-sizing: border-box;
  display: inline-block;
  transform: translateY(-12px);
  width: 315px;
  max-width: 94vw;
  filter: drop-shadow(0 4px 0 #929292);
}

.bubble-svg svg {
  width: 100%;
  height: auto;
  display: block;
}

/* テキストをSVGの上に重ねて表示（三角形部分を考慮） */
.bubble-content {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px 20px;
  box-sizing: border-box;
}

.bubble-text {
  font-size: 16px;
  line-height: 1.5;
  color: #111;
  text-align: center;
}

/* 既存のアニメーション */
@keyframes bubblePop {
  0% { 
    transform: translateY(6px) scale(0.98); 
    opacity: 0;
  }
  60% { 
    transform: translateY(-6px) scale(1.04); 
    opacity: 1;
  }
  100% { 
    transform: translateY(0) scale(1); 
    opacity: 1;
  }
}

.bubble-animate { 
  animation: bubblePop 420ms cubic-bezier(.22,.9,.5,1) both; 
  transform-origin: center top;
}
</style>