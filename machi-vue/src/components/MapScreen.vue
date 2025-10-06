<template>
  <div class="map-screen">
    <div id="map" ref="mapContainer"></div>
    
    <!-- デバッグパネル（デバッグモード時のみ表示） -->
    <div v-if="debugMode" class="debug-panel">
      <h4>🐛 デバッグモード</h4>
      <p>ステータス: {{ currentStatus }}</p>
      <div class="debug-info">
        <div>緯度: {{ currentPosition.lat?.toFixed(6) || '---' }}</div>
        <div>経度: {{ currentPosition.lng?.toFixed(6) || '---' }}</div>
        <div>精度: {{ currentPosition.accuracy?.toFixed(0) || '---' }}m</div>
        <div>次の目標まで: {{ distanceToNext?.toFixed(0) || '---' }}m</div>
      </div>
      <div class="debug-buttons">
        <button @click="showTutorial" class="debug-btn">チュートリアル表示</button>
        <button @click="setDebugPosition" class="debug-btn">現在位置をセット</button>
      </div>
    </div>
    
    <!-- 位置情報ステータス -->
    <div class="location-status">
      <div class="location-info">
        <span class="location-dot" :class="{ active: isLocationActive }"></span>
        <span>{{ locationStatusText }}</span>
      </div>
      <div v-if="routeProgress.total > 0" class="route-progress">
        ルート進行: {{ routeProgress.revealed }}/{{ routeProgress.total }}
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${routeProgress.percentage}%` }"
          ></div>
        </div>
      </div>
    </div>
    
    <!-- トランシーバーボタン -->
    <TransceiverButton 
      ref="transceiverButton"
      @hide="hideTransceiver"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import L from 'leaflet'
import TransceiverButton from './TransceiverButton.vue'

// 親コンポーネントとの通信
const emit = defineEmits(['show-tutorial'])

// テンプレート参照
const mapContainer = ref(null)
const transceiverButton = ref(null)

// 地図関連の状態
const map = ref(null)
const mapInitialized = ref(false)

// 位置追跡関連の状態
const currentPosition = ref({ lat: null, lng: null, accuracy: null })
const posCircle = ref(null)
const isLocationActive = ref(false)
const geolocationWatchId = ref(null)

// ルート関連の状態
const routeCoords = ref([])
const revealedIndex = ref(-1)
const visitedLine = ref(null)
const nextDestMarker = ref(null)
const todayRouteLayer = ref(null)
const distanceToNext = ref(null)

// デバッグ関連の状態
const debugMode = ref(false)
const currentStatus = ref('')
const debugMarker = ref(null)

// コメント関連の状態
const commentMarkers = ref({})

// 計算されたプロパティ
const locationStatusText = computed(() => {
  if (!isLocationActive.value) return '位置情報を取得中...'
  if (!currentPosition.value.lat) return '位置情報を取得中...'
  return `位置取得中 (±${currentPosition.value.accuracy?.toFixed(0) || '---'}m)`
})

const routeProgress = computed(() => {
  const total = routeCoords.value.length
  const revealed = Math.max(0, revealedIndex.value + 1)
  const percentage = total > 0 ? (revealed / total * 100) : 0
  return { total, revealed, percentage }
})

// 地図初期化
const initMap = () => {
  if (!mapContainer.value || mapInitialized.value) return
  
  mapInitialized.value = true
  
  map.value = L.map(mapContainer.value, {
    zoomControl: true,
    attributionControl: true
  }).setView([35.6812, 139.7671], 15)
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(map.value)
  
  console.log('地図が初期化されました')
  
  // 地図クリック処理（デバッグモード時のマーカー配置用）
  map.value.on('click', handleMapClick)
  
  // 位置情報取得開始
  startLocationTracking()
  
  // 既存のコメントを読み込み
  setTimeout(loadExistingComments, 500)
}

// 位置情報追跡開始
const startLocationTracking = () => {
  if (!navigator.geolocation) {
    console.warn('位置情報がサポートされていません')
    return
  }
  
  const geoOptions = {
    enableHighAccuracy: true,
    maximumAge: 1000,
    timeout: 10000
  }
  
  // 現在位置取得
  navigator.geolocation.getCurrentPosition(
    position => updatePosition(position.coords.latitude, position.coords.longitude, position.coords.accuracy),
    error => console.warn('位置情報取得エラー:', error),
    geoOptions
  )
  
  // 位置監視開始
  geolocationWatchId.value = navigator.geolocation.watchPosition(
    position => updatePosition(position.coords.latitude, position.coords.longitude, position.coords.accuracy),
    error => console.warn('位置情報監視エラー:', error),
    geoOptions
  )
}

// 現在位置更新
const updatePosition = (lat, lng, accuracy) => {
  if (!map.value) return
  
  try {
    // 位置情報の状態更新
    currentPosition.value = { lat, lng, accuracy }
    isLocationActive.value = true
    
    // 既存の位置円を削除
    if (posCircle.value) {
      map.value.removeLayer(posCircle.value)
    }
    
    // 新しい位置円を作成
    posCircle.value = L.circle([lat, lng], {
      radius: 12,
      color: '#00b0ff',
      fillColor: '#aee6ff',
      fillOpacity: 0.6
    }).addTo(map.value)
    
    // 地図を現在位置に移動
    map.value.panTo([lat, lng])
    
    // ルートとの近接判定
    evaluateProximity(lat, lng)
    
    console.log(`位置更新: ${lat.toFixed(6)}, ${lng.toFixed(6)} (±${accuracy?.toFixed(0)}m)`)
  } catch (error) {
    console.warn('位置更新エラー:', error)
  }
}

// 地図クリック処理（デバッグモード時のマーカー配置）
const handleMapClick = (e) => {
  console.log('Map clicked:', e.latlng)
  
  // デバッグモード時のマーカー配置
  if (debugMode.value) {
    placeDebugMarker(e.latlng.lat, e.latlng.lng)
  }
  
  // トランシーバーが引き出されている場合は隠す
  if (transceiverButton.value) {
    transceiverButton.value.hideTransceiver()
  }
}

// 今日のコース読み込み
const loadTodayCourse = async () => {
  try {
    // 今日のコース取得
    const res = await fetch('/api/class_course')
    if (!res.ok) return
    
    const data = await res.json()
    const courseId = data.course_id || data.course_of_day || null
    
    if (!courseId) return
    
    // コースのGPXデータ取得
    const courseRes = await fetch(`/api/courses/${courseId}`)
    if (!courseRes.ok) return
    
    const courseData = await courseRes.json()
    const gpxContent = courseData.gpx || courseData.content || courseData.gpx_content
    
    if (!gpxContent) return
    
    // GPXデータ解析
    const parser = new DOMParser()
    const gpxDoc = parser.parseFromString(gpxContent, 'text/xml')
    const trackPoints = gpxDoc.querySelectorAll('trkpt')
    
    if (!trackPoints || trackPoints.length === 0) return
    
    const coords = []
    trackPoints.forEach(pt => {
      const lat = parseFloat(pt.getAttribute('lat'))
      const lon = parseFloat(pt.getAttribute('lon'))
      if (!isNaN(lat) && !isNaN(lon)) {
        coords.push([lat, lon])
      }
    })
    
    if (coords.length === 0) return
    
    // ルート座標を保存
    routeCoords.value = coords
    revealedIndex.value = -1
    
    // 既存のルートレイヤーを削除
    clearRouteDisplay()
    
    // 最初の目標地点を表示
    showNextDestination()
    
    console.log(`今日のコース読み込み完了: ${coords.length}ポイント`)
  } catch (error) {
    console.warn('今日のコース読み込み失敗:', error)
  }
}

// ルート表示をクリア
const clearRouteDisplay = () => {
  if (todayRouteLayer.value) {
    try { map.value.removeLayer(todayRouteLayer.value) } catch (e) {}
    todayRouteLayer.value = null
  }
  if (visitedLine.value) {
    try { map.value.removeLayer(visitedLine.value) } catch (e) {}
    visitedLine.value = null
  }
  if (nextDestMarker.value) {
    try { map.value.removeLayer(nextDestMarker.value) } catch (e) {}
    nextDestMarker.value = null
  }
}

// 次の目標地点を表示
const showNextDestination = () => {
  if (!routeCoords.value || routeCoords.value.length === 0) return
  
  const nextIndex = revealedIndex.value + 1
  if (nextIndex >= routeCoords.value.length) {
    // すべて表示済み - フルルートを表示
    revealFullRoute()
    return
  }
  
  const [lat, lng] = routeCoords.value[nextIndex]
  
  // 既存の次目標マーカーを削除
  if (nextDestMarker.value) {
    try { map.value.removeLayer(nextDestMarker.value) } catch (e) {}
    nextDestMarker.value = null
  }
  
  // 目立つマーカーを作成
  const icon = L.divIcon({
    className: '',
    html: '<div class="next-dest-marker"></div>',
    iconSize: [26, 26],
    iconAnchor: [13, 13]
  })
  
  nextDestMarker.value = L.marker([lat, lng], { icon }).addTo(map.value)
  
  // 地図を目標地点に移動
  try { map.value.panTo([lat, lng]) } catch (e) {}
}

// 指定したインデックスまでのルートを表示
const revealUpToIndex = (index) => {
  if (index < 0) return
  
  const points = routeCoords.value.slice(0, index + 1)
  
  if (visitedLine.value) {
    try { map.value.removeLayer(visitedLine.value) } catch (e) {}
    visitedLine.value = null
  }
  
  visitedLine.value = L.polyline(points, {
    color: '#00b0ff',
    weight: 4,
    opacity: 0.9
  }).addTo(map.value)
}

// フルルートを表示
const revealFullRoute = () => {
  if (todayRouteLayer.value) return
  if (routeCoords.value.length === 0) return
  
  todayRouteLayer.value = L.polyline(routeCoords.value, {
    color: '#1976d2',
    weight: 4,
    opacity: 0.9
  }).addTo(map.value)
  
  // 次目標マーカーを削除
  if (nextDestMarker.value) {
    try { map.value.removeLayer(nextDestMarker.value) } catch (e) {}
    nextDestMarker.value = null
  }
  
  // 地図をルート全体に合わせる
  try {
    map.value.fitBounds(todayRouteLayer.value.getBounds(), { padding: [20, 20] })
  } catch (e) {}
}

// 距離計算（ハーバイサイン公式）
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

// 近接判定
const evaluateProximity = (lat, lng) => {
  if (!routeCoords.value || routeCoords.value.length === 0) return
  
  const nextIndex = revealedIndex.value + 1
  if (nextIndex >= routeCoords.value.length) return
  
  const [destLat, destLng] = routeCoords.value[nextIndex]
  const dist = haversineDistance(lat, lng, destLat, destLng)
  
  // 距離を更新
  distanceToNext.value = dist
  
  // 到着判定（20m以内）
  const ARRIVE_THRESHOLD = 20
  
  if (dist <= ARRIVE_THRESHOLD) {
    // 到着
    revealedIndex.value = nextIndex
    
    // 訪問済みルートを表示
    revealUpToIndex(revealedIndex.value)
    
    // 次の目標地点を表示
    showNextDestination()
    
    // 最後の地点に到達した場合はフルルート表示
    if (revealedIndex.value >= routeCoords.value.length - 1) {
      revealFullRoute()
    }
    
    console.log(`目標地点 ${nextIndex + 1} に到着!`)
  }
}

// デバッグマーカーの配置
const placeDebugMarker = (lat, lng) => {
  if (!debugMode.value) return
  
  // 既存のデバッグマーカーを削除
  if (debugMarker.value) {
    try { map.value.removeLayer(debugMarker.value) } catch (e) {}
    debugMarker.value = null
  }
  
  const icon = L.divIcon({
    className: '',
    html: '<div class="debug-marker"></div>',
    iconSize: [22, 22],
    iconAnchor: [11, 11]
  })
  
  debugMarker.value = L.marker([lat, lng], { icon }).addTo(map.value)
  
  // デバッグマーカーを現在位置として扱う
  updatePosition(lat, lng, 5)
}

// デバッグ関連のメソッド
const showTutorial = () => {
  // localStorageをクリアしてチュートリアルを表示
  localStorage.removeItem('studentUuid')
  localStorage.removeItem('studentName')
  emit('show-tutorial')
}

const setDebugPosition = () => {
  if (!map.value) return
  const center = map.value.getCenter()
  placeDebugMarker(center.lat, center.lng)
}

// デバッグモードチェック
const checkDebugMode = async () => {
  try {
    const res = await fetch('/api/status')
    if (!res.ok) return
    
    const data = await res.json()
    currentStatus.value = data.status || ''
    debugMode.value = currentStatus.value === 'デバッグ'
  } catch (error) {
    console.warn('デバッグモードチェック失敗:', error)
  }
}

// 既存のコメントを読み込み
const loadExistingComments = async () => {
  try {
    const res = await fetch('/api/comments')
    if (!res.ok) return
    
    const comments = await res.json()
    comments.forEach(comment => {
      if (!commentMarkers.value[comment.comment_id]) {
        addCommentMarker(comment)
      }
    })
  } catch (error) {
    console.warn('コメント読み込み失敗:', error)
  }
}

// コメントマーカーを追加
const addCommentMarker = (comment) => {
  try {
    const lat = comment.lat !== undefined && comment.lat !== null ? Number(comment.lat) : null
    const lng = comment.lon !== undefined && comment.lon !== null ? Number(comment.lon) : null
    
    if (lat === null || lng === null) return
    if (Number.isNaN(lat) || Number.isNaN(lng)) return
    if (commentMarkers.value[comment.comment_id]) return
    
    const iconHtml = `
      <div class="comment-marker">
        <div class="comment-marker-bg"></div>
        <div class="comment-marker-icon">★</div>
      </div>
    `
    
    const icon = L.divIcon({
      className: '',
      html: iconHtml,
      iconSize: [40, 40],
      iconAnchor: [20, 20]
    })
    
    const marker = L.marker([lat, lng], { icon, zIndexOffset: 1000 }).addTo(map.value)
    
    let timeStr = ''
    try {
      timeStr = comment.created_at ? new Date(comment.created_at).toLocaleString('ja-JP') : ''
    } catch (e) {}
    
    const popupHtml = `
      <div style="min-width:160px">
        <strong>${comment.user_id}</strong>
        ${timeStr ? `<div style="font-size:12px;color:#666">${timeStr}</div>` : ''}
        <div style="margin-top:6px">${comment.text}</div>
      </div>
    `
    
    marker.bindPopup(popupHtml)
    commentMarkers.value[comment.comment_id] = marker
  } catch (error) {
    console.warn('コメントマーカー追加失敗:', error)
  }
}

// 新しいコメントをポーリング
const pollNewComments = async () => {
  try {
    const res = await fetch('/api/comments')
    if (!res.ok) return
    
    const comments = await res.json()
    comments.forEach(comment => {
      if (!commentMarkers.value[comment.comment_id]) {
        addCommentMarker(comment)
      }
    })
  } catch (error) {
    console.warn('新しいコメントのポーリング失敗:', error)
  }
}

// トランシーバー表示制御
const hideTransceiver = () => {
  // TransceiverButton内で管理するため不要
}

// 定期更新
let debugModeInterval = null
let commentPollingInterval = null

onMounted(async () => {
  console.log('地図画面が表示されました')
  
  // 地図初期化（少し遅延させてDOMが準備されるのを待つ）
  setTimeout(async () => {
    initMap()
    await loadTodayCourse()
  }, 100)
  
  // デバッグモードチェック（10秒間隔）
  await checkDebugMode()
  debugModeInterval = setInterval(checkDebugMode, 10000)
  
  // 既存コメントの初期読み込み（地図初期化後）
  setTimeout(() => {
    if (mapInitialized.value) loadExistingComments()
  }, 1500)
  
  // コメントポーリング（5秒間隔、地図初期化後）
  setTimeout(() => {
    commentPollingInterval = setInterval(() => {
      if (mapInitialized.value) pollNewComments()
    }, 5000)
  }, 2000)
})

onUnmounted(() => {
  // 位置監視停止
  if (geolocationWatchId.value) {
    navigator.geolocation.clearWatch(geolocationWatchId.value)
  }
  
  // インターバル停止
  if (debugModeInterval) {
    clearInterval(debugModeInterval)
  }
  if (commentPollingInterval) {
    clearInterval(commentPollingInterval)
  }
  
  // 地図クリーンアップ
  if (map.value) {
    map.value.remove()
    map.value = null
  }
})
</script>

<style scoped>
.map-screen {
  width: 100vw;
  height: 100vh;
  position: relative;
}

#map {
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.status-overlay {
  position: fixed;
  top: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-width: 250px;
}

.debug-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  min-width: 200px;
}

.location-status {
  position: fixed;
  bottom: 120px;
  left: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-width: 250px;
}

.location-status.error {
  background: rgba(255, 235, 235, 0.95);
  border-left: 4px solid #f44336;
}

.route-progress {
  position: fixed;
  bottom: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-width: 250px;
}

:deep(.next-dest-marker) {
  width: 26px;
  height: 26px;
  background: radial-gradient(circle, #ff5722 0%, #d84315 100%);
  border: 3px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  animation: pulse-dest 2s infinite;
}

@keyframes pulse-dest {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

:deep(.debug-marker) {
  width: 22px;
  height: 22px;
  background: radial-gradient(circle, #9c27b0 0%, #7b1fa2 100%);
  border: 2px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

:deep(.comment-marker) {
  position: relative;
}

:deep(.comment-marker-bg) {
  width: 40px;
  height: 40px;
  background: radial-gradient(circle, #ffeb3b 0%, #fbc02d 100%);
  border: 2px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

:deep(.comment-marker-icon) {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 18px;
  color: #333;
  font-weight: bold;
}

.btn {
  background: #1976d2;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin: 4px;
}

.btn:hover {
  background: #1565c0;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}


</style>