import { ref, onMounted, onUnmounted } from 'vue'
import lottie from 'lottie-web'

export function useLottieAnimations() {
  const currentAnimationUrl = ref(null)
  const preloadedAnimations = ref({})
  const lottieAnim = ref(null)
  const isLoading = ref(true)

  // 既存のpreloadAllAnimations()ロジックを移植
  const preloadAllAnimations = async () => {
    if (typeof lottie === 'undefined' || !lottie) {
      setTimeout(preloadAllAnimations, 100)
      return
    }

    // ユニークなアニメーションURLを収集
    const animationUrls = [
      'https://lottie.host/f388a0b2-cce4-4681-a943-d8fb67a984d7/XfkX4AvJZo.json',
      'https://lottie.host/98be370f-0447-4347-b2c1-8256fc4c440d/HdoBME0ofD.json',
      'https://lottie.host/f26cbe82-399e-4375-aa69-d2f5ac331887/0wfU1QJrz7.json'
    ]

    console.log('Preloading animations:', animationUrls)
    
    let loadedCount = 0
    const loadPromises = animationUrls.map(url => 
      fetch(url)
        .then(r => r.json())
        .then(data => {
          preloadedAnimations.value[url] = data
          loadedCount++
          console.log(`Preloaded animation ${loadedCount}/${animationUrls.length}: ${url}`)
        })
        .catch(e => {
          console.warn('Failed to preload animation:', url, e)
          loadedCount++
        })
    )

    await Promise.all(loadPromises)
    isLoading.value = false
    console.log('All animations preloaded')
  }

  // キャラクターアニメーションを切り替え（既存ロジック移植）
  const switchToCharacter = (url, container) => {
    if (!url || url === currentAnimationUrl.value || !container) return

    try {
      // 既存のアニメーションを破棄
      if (lottieAnim.value) {
        try {
          lottieAnim.value.destroy()
        } catch (e) {
          console.warn('Failed to destroy previous animation:', e)
        }
      }

      // コンテナをクリア
      container.innerHTML = ''

      // プリロードされたデータを使用
      if (preloadedAnimations.value[url]) {
        lottieAnim.value = lottie.loadAnimation({
          container: container,
          renderer: 'svg',
          loop: false,
          autoplay: false,
          animationData: preloadedAnimations.value[url]
        })

        currentAnimationUrl.value = url
        console.log('Switched to preloaded character:', url)

        // アニメーション再生
        setTimeout(() => {
          if (lottieAnim.value) {
            try {
              lottieAnim.value.goToAndPlay(0, true)
            } catch (e) {
              console.warn('Failed to play animation:', e)
            }
          }
        }, 50)
      } else {
        // フォールバック: プレースホルダー表示
        console.warn('Animation not preloaded:', url)
        container.innerHTML = '<div style="font-size:48px;color:#666;display:flex;align-items:center;justify-content:center;width:100%;height:100%;">た</div>'
      }
    } catch (e) {
      console.warn('switchToCharacter error:', e)
    }
  }

  // アニメーションを再生
  const playAnimation = () => {
    if (lottieAnim.value) {
      try {
        lottieAnim.value.goToAndPlay(0, true)
        console.log('Lottie animation started from frame 0')
      } catch (e) {
        console.warn('Lottie play error:', e)
      }
    }
  }

  // クリーンアップ
  const cleanup = () => {
    if (lottieAnim.value) {
      try {
        lottieAnim.value.destroy()
      } catch (e) {
        console.warn('Failed to cleanup animation:', e)
      }
      lottieAnim.value = null
    }
  }

  onMounted(() => {
    preloadAllAnimations()
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    currentAnimationUrl,
    preloadedAnimations,
    isLoading,
    switchToCharacter,
    playAnimation,
    cleanup
  }
}