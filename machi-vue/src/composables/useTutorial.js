import { ref, computed } from 'vue'

// 既存のtutorialStoryデータを完全移植
export const tutorialStory = [
  { 
    title: 'たぬけん', 
    message: 'きょうは、たんけんをてつだいに\n来てくれて、ありがとう！', 
    character: 'https://lottie.host/f388a0b2-cce4-4681-a943-d8fb67a984d7/XfkX4AvJZo.json'
  },
  { 
    title: 'たぬけん', 
    message: 'ぼくは『たぬけん』！よろしくね！！', 
    character: 'https://lottie.host/f388a0b2-cce4-4681-a943-d8fb67a984d7/XfkX4AvJZo.json'
  },
  { 
    title: 'たぬけん', 
    message: 'きょうのたんけんルートは\n水にかんけいするいきもの。', 
    character: 'https://lottie.host/98be370f-0447-4347-b2c1-8256fc4c440d/HdoBME0ofD.json'
  },
  { 
    title: 'たぬけん', 
    message: 'けれど、そのいきものがだれか\nぼくにもわからないんだ...', 
    character: 'https://lottie.host/f26cbe82-399e-4375-aa69-d2f5ac331887/0wfU1QJrz7.json'
  },
  { 
    title: 'たぬけん', 
    message: '『気づき』をあつめていけば、\nだれかわかるかもしれないよ！', 
    character: 'https://lottie.host/98be370f-0447-4347-b2c1-8256fc4c440d/HdoBME0ofD.json'
  },
  { 
    title: 'たぬけん', 
    message: '『気づき』は、トランシーバーで\nぼくに報告してね！', 
    character: 'https://lottie.host/f388a0b2-cce4-4681-a943-d8fb67a984d7/XfkX4AvJZo.json'
  },
  { 
    title: 'たぬけん', 
    message: 'トランシーバーを用意して！', 
    character: 'https://lottie.host/98be370f-0447-4347-b2c1-8256fc4c440d/HdoBME0ofD.json'
  },
  { 
    title: 'たぬけん', 
    message: 'ボタンをおしながら\n「じゅんびOK！」といってみよう', 
    character: 'https://lottie.host/98be370f-0447-4347-b2c1-8256fc4c440d/HdoBME0ofD.json'
  },
  { 
    title: 'たぬけん', 
    message: 'さいごに、きみのなまえは？', 
    character: 'https://lottie.host/f388a0b2-cce4-4681-a943-d8fb67a984d7/XfkX4AvJZo.json',
    isNameInput: true
  },
  { 
    title: 'たぬけん', 
    message: 'それじゃあ、{name}\nきょうはよろしくね！', 
    character: 'https://lottie.host/f388a0b2-cce4-4681-a943-d8fb67a984d7/XfkX4AvJZo.json',
    isNameDisplay: true
  }
]

// チュートリアル管理のComposable
export function useTutorial() {
  const currentStep = ref(1) // 1ベースで開始
  const isCompleted = ref(false)
  const studentName = ref('')

  // 現在のステップデータを取得（computed）
  const currentStepData = computed(() => {
    const index = currentStep.value - 1 // 0ベースのインデックスに変換
    if (index < 0 || index >= tutorialStory.length) {
      return null
    }
    return tutorialStory[index]
  })

  // 次のステップに進む
  const nextStep = () => {
    if (currentStep.value < tutorialStory.length) {
      currentStep.value++
      console.log(`ステップ進行: ${currentStep.value}/${tutorialStory.length}`)
      // 最終ステップを超えた場合のみ完了フラグを設定
      if (currentStep.value > tutorialStory.length) {
        console.log('チュートリアル完了フラグ設定')
        isCompleted.value = true
      }
    } else {
      // チュートリアル完了
      console.log('チュートリアル完了（上限到達）')
      isCompleted.value = true
    }
  }

  // 前のステップに戻る
  const previousStep = () => {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  // 名前を設定して次のステップへ
  const setNameAndNext = (name) => {
    studentName.value = name
    localStorage.setItem('studentName', name)
    nextStep()
  }

  // チュートリアルをリセット
  const resetTutorial = () => {
    currentStep.value = 1
    isCompleted.value = false
    studentName.value = ''
  }

  // 名前置換されたメッセージを取得
  const getDisplayMessage = () => {
    const stepData = currentStepData.value
    if (!stepData) return ''
    
    if (stepData.isNameDisplay) {
      const name = studentName.value || localStorage.getItem('studentName') || 'たんけんたい'
      return stepData.message.replace('{name}', name)
    }
    
    return stepData.message
  }

  const totalSteps = tutorialStory.length
  console.log('useTutorial.js - tutorialStory.length:', totalSteps)
  
  return {
    currentStep,
    currentStepData,
    isCompleted,
    studentName,
    nextStep,
    previousStep,
    setNameAndNext,
    resetTutorial,
    getDisplayMessage,
    totalSteps
  }
}