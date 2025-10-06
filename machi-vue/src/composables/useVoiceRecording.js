import { ref, onUnmounted } from 'vue'

export function useVoiceRecording() {
  // 状態管理
  const isRecording = ref(false)
  const isProcessing = ref(false)
  const levelPercent = ref(0)
  const debugInfo = ref('')
  
  // 音声録音関連の変数
  let mediaStream = null
  let recorder = null
  let chunks = []
  let analyser = null
  let audioCtx = null
  let sourceNode = null
  let _measuring = false
  
  // 音量検出関連
  let lastRms = 0
  let maxRms = 0
  let ambientRms = 0
  let dynamicThreshold = 0.005
  
  // グローバル状態保持（キャリブレーション履歴）
  if (typeof window !== 'undefined') {
    window._prevAmbientRms = window._prevAmbientRms || null
    window._prevDynamicThreshold = window._prevDynamicThreshold || null
  }

  // 環境音キャリブレーション
  const calibrateAmbient = async (durationMs = 300) => {
    if (!analyser || !audioCtx) return
    
    const tmp = new Float32Array(analyser.fftSize)
    const samples = []
    const start = performance.now()
    
    while (performance.now() - start < durationMs) {
      analyser.getFloatTimeDomainData(tmp)
      let sum = 0
      for (let i = 0; i < tmp.length; i++) {
        const v = tmp[i]
        sum += v * v
      }
      const rms = Math.sqrt(sum / tmp.length)
      samples.push(rms)
      await new Promise(r => setTimeout(r, 20))
    }
    
    // 下半分の平均を取得（ノイズを除外）
    samples.sort((a, b) => a - b)
    const half = Math.floor(samples.length / 2) || 1
    let sumLow = 0
    for (let i = 0; i < half; i++) {
      sumLow += samples[i]
    }
    const lowerMean = sumLow / half
    let ambientCandidate = lowerMean
    
    // 前回の値とスムージング
    if (typeof window !== 'undefined' && typeof window._prevAmbientRms === 'number' && window._prevAmbientRms > 0) {
      ambientRms = window._prevAmbientRms * 0.7 + ambientCandidate * 0.3
    } else {
      ambientRms = ambientCandidate
    }
    if (typeof window !== 'undefined') {
      window._prevAmbientRms = ambientRms
    }
    
    // 動的閾値設定
    const newThreshold = Math.max(ambientRms * 3.0, 0.0003)
    if (typeof window !== 'undefined' && typeof window._prevDynamicThreshold === 'number' && window._prevDynamicThreshold > 0) {
      dynamicThreshold = Math.min(newThreshold, window._prevDynamicThreshold * 3)
    } else {
      dynamicThreshold = newThreshold
    }
    if (typeof window !== 'undefined') {
      window._prevDynamicThreshold = dynamicThreshold
    }
    
    console.log('[calibrateAmbient] ambientRms=', ambientRms, 'threshold=', dynamicThreshold)
  }

  // 音量レベル更新
  const updateMeter = (rms) => {
    try {
      const denom = dynamicThreshold || 0.0003
      const ratio = rms / denom
      const pct = Math.min(1, Math.sqrt(Math.max(0, ratio)) * 0.95)
      
      levelPercent.value = pct * 100
      debugInfo.value = `rms:${rms.toFixed(5)} ambient:${ambientRms.toFixed(5)} thr:${dynamicThreshold.toFixed(5)}`
    } catch (e) {
      // ignore
    }
  }

  // 音量測定
  const measureSilence = () => {
    if (!analyser || !audioCtx) return
    _measuring = true
    const buf = new Float32Array(analyser.fftSize)
    
    const loop = () => {
      analyser.getFloatTimeDomainData(buf)
      let sum = 0
      for (let i = 0; i < buf.length; i++) {
        const v = buf[i]
        sum += v * v
      }
      const rms = Math.sqrt(sum / buf.length)
      lastRms = rms
      
      // セッション中の最大値更新
      if (rms > maxRms) maxRms = rms
      
      // メーター更新
      updateMeter(rms)
      
      if (_measuring) requestAnimationFrame(loop)
    }
    requestAnimationFrame(loop)
  }

  // 録音開始
  const startRecording = async () => {
    try {
      isRecording.value = true
      
      if (!mediaStream) {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      }
      
      // AudioContextとAnalyserを新規作成
      try {
        if (audioCtx) {
          try { audioCtx.close() } catch (_) {}
        }
      } catch (e) {}
      
      audioCtx = new (window.AudioContext || window.webkitAudioContext)()
      
      try {
        sourceNode = audioCtx.createMediaStreamSource(mediaStream)
      } catch (e) {
        console.warn('createMediaStreamSource failed', e)
        sourceNode = null
      }
      
      analyser = audioCtx.createAnalyser()
      analyser.fftSize = 2048
      
      try {
        if (sourceNode && analyser) sourceNode.connect(analyser)
      } catch (e) {
        // ignore
      }
      
      // 環境音キャリブレーション
      await calibrateAmbient(300)
      
      // ピークトラッカーリセット
      maxRms = 0
      
      recorder = new MediaRecorder(mediaStream)
      chunks = []
      recorder.ondataavailable = ev => chunks.push(ev.data)
      recorder.start()
      
      // 音量測定開始
      measureSilence()
      
    } catch (err) {
      console.error(err)
      isRecording.value = false
      throw new Error('マイクへのアクセスが許可されていません')
    }
  }

  // 録音停止と送信
  const stopRecording = async () => {
    return new Promise((resolve, reject) => {
      if (!recorder) {
        reject(new Error('録音が開始されていません'))
        return
      }
      
      isRecording.value = false
      isProcessing.value = true
      
      recorder.onstop = async () => {
        try {
          _measuring = false
          
          // リソースクリーンアップ
          if (sourceNode) {
            try { sourceNode.disconnect() } catch (_) {}
            sourceNode = null
          }
          if (audioCtx) {
            try { audioCtx.close() } catch (_) {}
            audioCtx = null
          }
          
          if (!chunks || chunks.length === 0) {
            throw new Error('録音データがありません')
          }
          
          const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' })
          
          // 音量チェック（無音判定）
          console.log('[stopRecording] lastRms=', lastRms, 'maxRms=', maxRms, 'dynamicThreshold=', dynamicThreshold)
          
          const peakRequired = dynamicThreshold * 0.8
          if (lastRms < dynamicThreshold && maxRms < peakRequired) {
            throw new Error('音声が検出されませんでした。もう一度大きな声で話してください。')
          }
          
          // Groq APIに音声を送信
          const fd = new FormData()
          fd.append('file', blob, 'voice.webm')
          
          const res = await fetch('/api/groq/audio', { method: 'POST', body: fd })
          if (!res.ok) throw new Error('音声送信失敗')
          
          const j = await res.json()
          const transcript = (j.transcript || '').trim()
          
          if (!transcript) {
            throw new Error('音声認識できませんでした。もう一度ゆっくり話してみてください。')
          }
          
          // テキスト解析APIに送信
          const r2 = await fetch('/api/groq/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: transcript })
          })
          
          if (!r2.ok) throw new Error('返信取得失敗')
          
          const jr = await r2.json()
          
          resolve({
            transcript,
            response: jr.output || '応答がありません'
          })
          
        } catch (err) {
          reject(err)
        } finally {
          isProcessing.value = false
        }
      }
      
      // 録音停止
      try {
        recorder.stop()
      } catch (err) {
        console.error('recorder.stop error', err)
        isProcessing.value = false
        reject(err)
      }
    })
  }

  // コメント保存
  const saveComment = async (text) => {
    try {
      const studentUuid = localStorage.getItem('studentUuid')
      const studentName = localStorage.getItem('studentName') || 'Unknown'
      
      if (!studentUuid) {
        console.warn('Student UUID not found')
        return
      }
      
      const payload = {
        student_id: studentUuid,
        student_name: studentName,
        content: text,
        latitude: null,
        longitude: null
      }
      
      const res = await fetch('/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      
      if (!res.ok) {
        throw new Error(`Comment save failed: ${res.status}`)
      }
      
      console.log('Comment saved successfully')
    } catch (err) {
      console.warn('saveComment failed', err)
      throw err
    }
  }

  // クリーンアップ
  const cleanup = () => {
    _measuring = false
    if (sourceNode) {
      try { sourceNode.disconnect() } catch (_) {}
    }
    if (audioCtx) {
      try { audioCtx.close() } catch (_) {}
    }
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
    }
  }

  // コンポーネントアンマウント時のクリーンアップ
  onUnmounted(() => {
    cleanup()
  })

  return {
    // 状態
    isRecording,
    isProcessing,
    levelPercent,
    debugInfo,
    
    // メソッド
    startRecording,
    stopRecording,
    saveComment,
    cleanup
  }
}