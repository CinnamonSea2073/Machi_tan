<template>
  <div class="result-screen">
    <div class="result-container">
      <!-- ヘッダー -->
      <div class="result-header">
        <h1 class="result-title">
          お疲れ様でした！<br>
          <span class="student-name">{{ studentName }}</span>さん
        </h1>
        <div class="completion-badge">
          🎉 ミッション完了！ 🎉
        </div>
      </div>

      <!-- 統計情報 -->
      <div class="stats-grid">
        <!-- 歩行距離 -->
        <div class="stat-card">
          <div class="stat-icon">👟</div>
          <div class="stat-content">
            <div class="stat-label">{{ studentName }}さんが歩いた距離</div>
            <div class="stat-value">{{ formatDistance(totalDistance) }}</div>
          </div>
        </div>

        <!-- 訪問ポイント -->
        <div class="stat-card">
          <div class="stat-icon">📍</div>
          <div class="stat-content">
            <div class="stat-label">{{ studentName }}さんが到達した地点</div>
            <div class="stat-value">{{ visitedPoints }} / {{ totalPoints }} 地点</div>
          </div>
        </div>

        <!-- コメント数 -->
        <div class="stat-card">
          <div class="stat-icon">💬</div>
          <div class="stat-content">
            <div class="stat-label">{{ studentName }}さんのコメント</div>
            <div class="stat-value">{{ commentCount }} 件</div>
          </div>
        </div>

        <!-- 活動時間 -->
        <div class="stat-card">
          <div class="stat-icon">⏱️</div>
          <div class="stat-content">
            <div class="stat-label">{{ studentName }}さんの活動時間</div>
            <div class="stat-value">{{ formatDuration(activityDuration) }}</div>
          </div>
        </div>
      </div>

      <!-- コメント履歴 -->
      <div v-if="userComments.length > 0" class="comments-section">
        <h2 class="section-title">{{ studentName }}さんのコメント履歴</h2>
        <div class="comments-list">
          <div 
            v-for="comment in userComments" 
            :key="comment.comment_id"
            class="comment-item"
          >
            <div class="comment-time">
              {{ formatCommentTime(comment.created_at) }}
            </div>
            <div class="comment-text">
              "{{ comment.text }}"
            </div>
          </div>
        </div>
      </div>

      <!-- ルート概要 -->
      <div class="route-section">
        <h2 class="section-title">{{ studentName }}さんが歩いたルート</h2>
        <div class="route-summary">
          <div v-if="routeCoords.length > 0" class="route-description">
            {{ studentName }}さんは {{ routeCoords.length }} 個のポイントを通って、
            素晴らしい街歩きを完成させました！
          </div>
          <div v-else class="route-description">
            今回の街歩きデータを準備中です...
          </div>
        </div>
      </div>

      <!-- メッセージ -->
      <div class="final-message">
        <p>
          {{ studentName }}さん、今日は街歩きに参加してくれてありがとうございました！<br>
          みんなで歩いた思い出は、きっと特別なものになったはずです。<br>
          また一緒に街を探検しましょう！
        </p>
      </div>

      <!-- アクションボタン -->
      <div class="action-buttons">
        <button @click="shareResult" class="share-btn">
          📤 結果をシェア
        </button>
        <button @click="backToTop" class="back-btn">
          🏠 最初に戻る
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Props
const props = defineProps({
  studentName: {
    type: String,
    default: '匿名ユーザー'
  }
})

// 状態管理
const totalDistance = ref(0)
const visitedPoints = ref(0)
const totalPoints = ref(0)
const commentCount = ref(0)
const activityDuration = ref(0)
const userComments = ref([])
const routeCoords = ref([])

// 計算プロパティ
const completionRate = computed(() => {
  if (totalPoints.value === 0) return 0
  return Math.round((visitedPoints.value / totalPoints.value) * 100)
})

// データ取得
const loadResultData = async () => {
  try {
    const studentUuid = localStorage.getItem('studentUuid')
    if (!studentUuid) return
    
    // コメント履歴を取得
    const commentsRes = await fetch('/api/comments')
    if (commentsRes.ok) {
      const allComments = await commentsRes.json()
      userComments.value = allComments.filter(c => c.user_id === studentUuid)
      commentCount.value = userComments.value.length
    }
    
    // 今日のコース情報を取得
    const courseRes = await fetch('/api/class_course')
    if (courseRes.ok) {
      const courseData = await courseRes.json()
      const courseId = courseData.course_id || courseData.course_of_day
      
      if (courseId) {
        const detailRes = await fetch(`/api/courses/${courseId}`)
        if (detailRes.ok) {
          const courseDetail = await detailRes.json()
          const gpxContent = courseDetail.gpx || courseDetail.content
          
          if (gpxContent) {
            const parser = new DOMParser()
            const gpxDoc = parser.parseFromString(gpxContent, 'text/xml')
            const trackPoints = gpxDoc.querySelectorAll('trkpt')
            
            routeCoords.value = Array.from(trackPoints).map(pt => ({
              lat: parseFloat(pt.getAttribute('lat')),
              lng: parseFloat(pt.getAttribute('lon'))
            }))
            
            totalPoints.value = routeCoords.value.length
            
            // 仮の進捗データ（実際の実装では、ユーザーの位置履歴から計算）
            visitedPoints.value = Math.floor(totalPoints.value * 0.8) // 80%完了と仮定
            totalDistance.value = calculateRouteDistance()
          }
        }
      }
    }
    
    // 活動時間を仮設定（実際の実装では、開始時刻から終了時刻を計算）
    activityDuration.value = 45 * 60 // 45分と仮定
    
  } catch (error) {
    console.warn('結果データの読み込みに失敗しました:', error)
  }
}

// ルートの総距離を計算（簡易版）
const calculateRouteDistance = () => {
  if (routeCoords.value.length < 2) return 0
  
  let distance = 0
  for (let i = 1; i < routeCoords.value.length; i++) {
    const prev = routeCoords.value[i - 1]
    const curr = routeCoords.value[i]
    distance += haversineDistance(prev.lat, prev.lng, curr.lat, curr.lng)
  }
  
  return distance
}

// ハーバーサイン距離計算
const haversineDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371000 // 地球の半径（メートル）
  const toRad = (value) => value * Math.PI / 180
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

// フォーマット関数
const formatDistance = (meters) => {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(1)} km`
  }
  return `${Math.round(meters)} m`
}

const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}時間${minutes}分`
  }
  return `${minutes}分`
}

const formatCommentTime = (dateString) => {
  try {
    const date = new Date(dateString)
    return date.toLocaleTimeString('ja-JP', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  } catch (e) {
    return ''
  }
}

// アクション
const shareResult = () => {
  // 結果をシェア（実装例）
  const text = `街歩きを完了しました！\n歩いた距離: ${formatDistance(totalDistance.value)}\n到達地点: ${visitedPoints.value}/${totalPoints.value}\nコメント: ${commentCount.value}件`
  
  if (navigator.share) {
    navigator.share({
      title: '街歩きの結果',
      text: text
    }).catch(err => console.log('シェアに失敗:', err))
  } else {
    // フォールバック: クリップボードにコピー
    navigator.clipboard.writeText(text).then(() => {
      alert('結果をクリップボードにコピーしました！')
    }).catch(err => {
      console.log('コピーに失敗:', err)
      alert(text)
    })
  }
}

const backToTop = () => {
  // ローカルストレージをクリアして最初から開始
  localStorage.removeItem('studentUuid')
  localStorage.removeItem('studentName')
  window.location.reload()
}

// マウント時に初期化
onMounted(() => {
  loadResultData()
})
</script>

<style scoped>
.result-screen {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow-y: auto;
  color: white;
}

.result-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.result-header {
  text-align: center;
  margin-bottom: 40px;
  padding-top: 20px;
}

.result-title {
  font-size: 2.2rem;
  font-weight: bold;
  margin: 0 0 20px 0;
  line-height: 1.4;
}

.student-name {
  color: #ffeb3b;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.completion-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0 auto;
  display: inline-block;
  backdrop-filter: blur(10px);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 30px 0 20px 0;
  text-align: center;
}

.comments-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.comment-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 15px;
}

.comment-time {
  font-size: 0.8rem;
  opacity: 0.7;
  margin-bottom: 5px;
}

.comment-text {
  font-style: italic;
  line-height: 1.4;
}

.route-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
}

.route-description {
  text-align: center;
  font-size: 1.1rem;
  line-height: 1.6;
}

.final-message {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
  text-align: center;
  font-size: 1.1rem;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: auto;
  padding: 20px 0;
}

.share-btn, .back-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.share-btn {
  background: #4caf50;
  color: white;
}

.share-btn:hover {
  background: #45a049;
  transform: translateY(-2px);
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .result-container {
    padding: 15px;
  }
  
  .result-title {
    font-size: 1.8rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .stat-card {
    padding: 15px;
    gap: 12px;
  }
  
  .stat-icon {
    font-size: 2rem;
  }
  
  .stat-value {
    font-size: 1.3rem;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .share-btn, .back-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>