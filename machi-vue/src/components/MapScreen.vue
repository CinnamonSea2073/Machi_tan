<template>
  <div class="map-screen">
    <div id="map" ref="mapContainer"></div>
    <div class="status-overlay">
      <h3>🗺️ Vue版地図画面</h3>
      <p>✅ Leaflet地図統合完了</p>
      <p>ユーザー: {{ studentName }}</p>
      <p><small>位置情報を取得中...</small></p>
    </div>
    
    <!-- 音声ボタン -->
    <VoiceButton :showDebug="showDebugInfo" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import VoiceButton from './VoiceButton.vue'

const mapContainer = ref(null)
const studentName = ref('')
const map = ref(null)
const posCircle = ref(null)
const showDebugInfo = ref(false)

// 既存のstudent.htmlから地図初期化ロジックを移植
const initMap = () => {
  if (!mapContainer.value || map.value) return
  
  map.value = L.map(mapContainer.value, {
    zoomControl: true,
    attributionControl: true
  }).setView([35.6812, 139.7671], 15)
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(map.value)
  
  console.log('Leaflet地図が初期化されました')
  
  // 現在位置取得を試行
  if (navigator.geolocation) {
    const geoOptions = { 
      enableHighAccuracy: true, 
      maximumAge: 1000, 
      timeout: 10000 
    }
    
    navigator.geolocation.getCurrentPosition(
      position => updatePosition(position.coords.latitude, position.coords.longitude),
      error => console.warn('位置情報取得エラー:', error),
      geoOptions
    )
  }
}

// 現在位置更新（既存ロジック移植）
const updatePosition = (lat, lon) => {
  if (!map.value) return
  
  try {
    if (posCircle.value) {
      map.value.removeLayer(posCircle.value)
    }
    
    posCircle.value = L.circle([lat, lon], {
      radius: 12,
      color: '#00b0ff',
      fillColor: '#aee6ff',
      fillOpacity: 0.6
    }).addTo(map.value)
    
    map.value.panTo([lat, lon])
    console.log('現在位置更新:', lat, lon)
  } catch (error) {
    console.warn('位置更新エラー:', error)
  }
}

onMounted(() => {
  // localStorageから学生名を取得
  studentName.value = localStorage.getItem('studentName') || '未登録'
  
  // デバッグモード検出
  showDebugInfo.value = new URLSearchParams(window.location.search).has('debug')
  
  // 地図初期化（少し遅延させてDOMが準備されるのを待つ）
  setTimeout(initMap, 100)
  
  console.log('地図画面が表示されました')
  console.log('学生名:', studentName.value)
  console.log('デバッグモード:', showDebugInfo.value)
})

onUnmounted(() => {
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


</style>