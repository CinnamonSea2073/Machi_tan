<template>
  <div class="name-input-form">
    <form @submit.prevent="handleSubmit" class="form-container">
      <div class="input-group">
        <label for="nameInput" class="input-label">お名前を入力してください</label>
        <input
          id="nameInput"
          v-model="inputName"
          type="text"
          class="name-input"
          placeholder="あなたのお名前"
          maxlength="20"
          @input="validateInput"
          :class="{ error: hasError }"
        />
        <div v-if="hasError" class="error-message">
          {{ errorMessage }}
        </div>
      </div>
      
      <button 
        type="submit" 
        class="submit-button"
        :disabled="!isValidName || isSubmitting"
      >
        <span v-if="isSubmitting">登録中...</span>
        <span v-else>次へ</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['submit'])

const inputName = ref('')
const isSubmitting = ref(false)
const hasError = ref(false)
const errorMessage = ref('')

const isValidName = computed(() => {
  return inputName.value.trim().length > 0 && inputName.value.trim().length <= 20
})

const validateInput = () => {
  const trimmedName = inputName.value.trim()
  
  if (trimmedName.length === 0) {
    hasError.value = false
    errorMessage.value = ''
    return
  }
  
  if (trimmedName.length > 20) {
    hasError.value = true
    errorMessage.value = '名前は20文字以内で入力してください'
    return
  }
  
  // より緩い文字チェック（基本的な記号のみ制限）
  if (/[<>{}[\]\\|`~!@#$%^&*()_+=;:'"?/.,]/.test(trimmedName)) {
    hasError.value = true
    errorMessage.value = '記号は使用できません'
    return
  }
  
  hasError.value = false
  errorMessage.value = ''
}

const handleSubmit = async () => {
  if (!isValidName.value || isSubmitting.value) return
  
  const trimmedName = inputName.value.trim()
  
  try {
    isSubmitting.value = true
    
    // 名前をlocalStorageに保存
    localStorage.setItem('studentName', trimmedName)
    
    // 短い遅延を入れてユーザビリティを向上
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 親コンポーネントに名前を送信
    emit('submit', trimmedName)
    
  } catch (error) {
    console.error('名前の保存に失敗しました:', error)
    hasError.value = true
    errorMessage.value = '名前の保存に失敗しました。もう一度お試しください。'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.name-input-form {
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
  padding: 0;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  text-align: center;
}

.name-input {
  width: 100%;
  height: 48px;
  padding: 12px 16px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 16px;
  text-align: center;
  box-sizing: border-box;
}

.name-input:focus {
  outline: none;
  border-color: #4caf50;
}

.name-input.error {
  border-color: #f44336;
}

.name-input.error:focus {
  border-color: #f44336;
}

.error-message {
  color: #f44336;
  font-size: 14px;
  text-align: center;
  margin-top: 4px;
}

.submit-button {
  height: 48px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 12px;
}

.submit-button:hover:not(:disabled) {
  background: #45a049;
}

.submit-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>