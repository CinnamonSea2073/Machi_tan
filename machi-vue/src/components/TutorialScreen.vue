<template>
  <div class="tutorial-screen" @click="handleScreenClick" @touchend="handleScreenClick">
    <div class="tutorial-container">
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
      <div v-if="!isNameInputStep" class="tutorial-hint">
        どこでもタップで次へ
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import CharacterContainer from './CharacterContainer.vue'
import TutorialBubble from './TutorialBubble.vue'
import NameInputForm from './NameInputForm.vue'
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
const handleScreenClick = async () => {
  console.log('画面クリック検出')
  console.log(`名前入力ステップ?: ${isNameInputStep.value}`)
  console.log(`現在のステップ: ${currentStep.value}`)
  console.log(`現在のステップデータ:`, currentStepData.value)
  
  // Step9（isNameInput: true）の時のみクリック無効
  if (isNameInputStep.value) {
    console.log('名前入力中のためクリック無効')
    return
  }
  
  console.log('nextStep()を実行')
  await nextStep()
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

// チュートリアル完了処理
const handleTutorialComplete = async () => {
  console.log('チュートリアル完了処理を開始')
  try {
    // 完了をlocalStorageに記録
    localStorage.setItem('tutorialCompleted', 'true')
    localStorage.setItem('tutorialCompletedAt', new Date().toISOString())
    
    console.log('地図画面に遷移します')
    // 親コンポーネントに完了を通知
    emit('complete')
    
  } catch (error) {
    console.error('チュートリアル完了処理エラー:', error)
    // エラーでも進行
    emit('complete')
  }
}

// 初期化
onMounted(() => {
  console.log('チュートリアル開始')
  console.log('TutorialScreen - totalSteps:', totalSteps.value)
  console.log('TutorialScreen - currentStep:', currentStep.value)
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
</style>