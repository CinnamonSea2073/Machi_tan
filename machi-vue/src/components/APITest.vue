<template>
  <div class="api-test">
    <h3>🔗 API統合テスト</h3>
    <button @click="testHealthcheck" :disabled="loading">
      ヘルスチェック
    </button>
    <button @click="testStudentAPI" :disabled="loading">
      学生API
    </button>
    <div v-if="result" class="result">
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const loading = ref(false)
const result = ref('')

const testHealthcheck = async () => {
  loading.value = true
  result.value = ''
  
  try {
    const response = await fetch('/api/healthz')
    const data = await response.json()
    result.value = `✅ ヘルスチェック成功:\n${JSON.stringify(data, null, 2)}`
  } catch (error) {
    result.value = `❌ ヘルスチェック失敗:\n${error.message}`
  } finally {
    loading.value = false
  }
}

const testStudentAPI = async () => {
  loading.value = true
  result.value = ''
  
  try {
    const response = await fetch('/api/students')
    const data = await response.json()
    result.value = `✅ 学生API成功:\n${JSON.stringify(data, null, 2)}`
  } catch (error) {
    result.value = `❌ 学生API失敗:\n${error.message}`
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.api-test {
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 20px;
}

button {
  margin-right: 10px;
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.result {
  margin-top: 20px;
  padding: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #ddd;
}

pre {
  margin: 0;
  font-size: 12px;
}
</style>