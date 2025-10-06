<template>
  <div class="debug-panel">
    <h4>🔧 デバッグパネル (Vue版)</h4>
    <button @click="$emit('show-tutorial')" class="debug-btn">
      チュートリアルを再表示
    </button>
    <button @click="$emit('show-map')" class="debug-btn">
      地図ページへ移動
    </button>
    <button @click="resetData" class="debug-btn">
      データリセット
    </button>
  </div>
</template>

<script setup>
// イベント定義
defineEmits(['show-tutorial', 'show-map'])

const resetData = () => {
  localStorage.removeItem('studentUuid')
  localStorage.removeItem('studentName')
  console.log('ローカルデータをリセットしました')
  location.reload()
}
</script>

<style scoped>
.debug-panel {
  position: fixed;
  left: 12px;
  top: 12px;
  z-index: 10000;
  background: rgba(0, 0, 0, 0.85);
  color: #fff;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  font-size: 14px;
}

.debug-btn {
  display: block;
  width: 100%;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #4caf50;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.debug-btn:hover {
  background: #45a049;
}

.debug-btn:last-child {
  background: #f44336;
}

.debug-btn:last-child:hover {
  background: #da190b;
}
</style>