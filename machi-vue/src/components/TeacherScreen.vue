<template>
  <div class="teacher-screen">
    <div class="container">
      <!-- ヘッダー -->
      <div class="header">
        <div class="h1">先生用ダッシュボード 📚</div>
        <button class="btn btn-small" @click="refreshAll">🔄 全更新</button>
      </div>

      <!-- GPXアップロード -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">コース登録（GPX）</div>
        </div>
        <div class="row">
          <input 
            type="file" 
            ref="gpxFileInput"
            class="col" 
            accept=".gpx" 
            @change="handleFileSelect"
          />
          <button 
            class="btn" 
            @click="uploadGpxFile"
            :disabled="uploading || !selectedFile"
          >
            {{ uploading ? 'アップロード中...' : '📤 アップロード' }}
          </button>
        </div>
      </div>

      <!-- コース一覧 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">コース一覧</div>
          <button class="btn btn-small" @click="loadCourses">更新</button>
        </div>
        <div class="list">
          <div v-if="courses.length === 0" class="empty-state">
            コースがまだ登録されていません
          </div>
          <div v-else>
            <div 
              v-for="course in courses" 
              :key="course.course_id" 
              class="course-item"
            >
              <div>
                <span class="course-id">{{ course.course_id }}</span>
                <br>
                <span class="course-meta">{{ formatDate(course.created_at) }}</span>
              </div>
              <div class="course-item-actions">
                <button 
                  class="btn btn-small" 
                  @click="previewCourse(course.course_id)"
                >
                  🗺️ プレビュー
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 当日のコース設定 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">当日のコース設定</div>
        </div>
        <div class="row">
          <select v-model="selectedTodayCourse" class="input col">
            <option value="">-- 選択してください --</option>
            <option 
              v-for="course in courses" 
              :key="course.course_id" 
              :value="course.course_id"
            >
              {{ course.course_id }}
            </option>
          </select>
          <button 
            class="btn" 
            @click="setTodayCourse"
            :disabled="!selectedTodayCourse"
          >
            ✓ 設定
          </button>
        </div>
        <div class="info-box" style="margin-top: 12px;">
          {{ todayInfo }}
        </div>
      </div>

      <!-- ステータス管理 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">ステータス管理</div>
          <button class="btn btn-small" @click="loadStatus">更新</button>
        </div>
        <div class="row" style="margin-bottom: 12px;">
          <select v-model="selectedStatus" class="input col">
            <option value="">-- ステータスを選択 --</option>
            <option value="デバッグ">🛠️ デバッグ（開発者向け）</option>
            <option value="チュートリアル">📚 チュートリアル（準備開始）</option>
            <option value="実行中">🗺️ 実行中（GPS アート開始）</option>
            <option value="終了">⏹️ 終了（活動停止）</option>
            <option value="結果">🎉 結果（リザルト表示）</option>
          </select>
          <button 
            class="btn" 
            @click="setStatus"
            :disabled="!selectedStatus"
          >
            ✓ 設定
          </button>
        </div>
        <div class="info-box">
          現在のステータス: <strong>{{ currentStatus || '未設定' }}</strong>
        </div>
      </div>

      <!-- 生徒のコメント -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">生徒のコメント（最新）</div>
          <button class="btn btn-small" @click="loadComments">更新</button>
        </div>
        <div class="list">
          <div v-if="comments.length === 0" class="empty-state">
            まだコメントがありません
          </div>
          <div v-else>
            <div v-for="comment in comments.slice(0, 50)" :key="comment.comment_id" class="comment-item">
              <div class="comment-meta">
                {{ formatDate(comment.created_at) }} | <strong>{{ comment.student_name || comment.user_id || 'anonymous' }}</strong>
              </div>
              <div>{{ comment.text }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- コースプレビューモーダル -->
    <div v-if="showPreviewModal" class="course-modal" @click.self="closePreviewModal">
      <div class="course-modal-content">
        <div class="course-modal-header">
          <h3>コースプレビュー: {{ previewCourseId }}</h3>
          <button class="btn btn-small" @click="closePreviewModal">✕ 閉じる</button>
        </div>
        <div ref="previewMapContainer" class="preview-map"></div>
        <div v-if="previewError" class="error-message">
          エラー: {{ previewError }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import L from 'leaflet'

// データの状態
const courses = ref([])
const comments = ref([])
const currentStatus = ref('')
const todayInfo = ref('❌ 今日のコースは未設定です')

// UI状態
const uploading = ref(false)
const selectedFile = ref(null)
const selectedTodayCourse = ref('')
const selectedStatus = ref('')

// モーダル状態
const showPreviewModal = ref(false)
const previewCourseId = ref('')
const previewError = ref('')
const previewMap = ref(null)

// テンプレート参照
const gpxFileInput = ref(null)
const previewMapContainer = ref(null)

// ユーティリティ関数
const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return new Date(dateString).toLocaleString('ja-JP')
  } catch (e) {
    return dateString
  }
}

// API呼び出しヘルパー
const apiCall = async (url, options = {}) => {
  try {
    // リクエストヘッダーを準備
    const headers = { ...options.headers }
    
    // POST/PUT/PATCHリクエストでbodyがある場合のみContent-Typeを設定
    if (options.method && ['POST', 'PUT', 'PATCH'].includes(options.method.toUpperCase()) && options.body) {
      headers['Content-Type'] = 'application/json'
    }
    
    const response = await fetch(url, {
      ...options,
      headers
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP ${response.status}: ${response.statusText}${errorText ? ` - ${errorText}` : ''}`)
    }
    
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await response.json()
    }
    
    return await response.text()
  } catch (error) {
    console.error('API call failed:', error)
    throw error
  }
}

// ファイル選択処理
const handleFileSelect = (event) => {
  const files = event.target.files
  selectedFile.value = files && files.length > 0 ? files[0] : null
}

// GPXファイルアップロード
const uploadGpxFile = async () => {
  if (!selectedFile.value) {
    alert('ファイルを選択してください')
    return
  }
  
  uploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    await fetch('/api/courses', {
      method: 'POST',
      body: formData
    })
    
    alert('✅ アップロード完了')
    selectedFile.value = null
    if (gpxFileInput.value) gpxFileInput.value.value = ''
    await loadCourses()
  } catch (error) {
    console.error('Upload failed:', error)
    alert(`❌ アップロード失敗: ${error.message}`)
  } finally {
    uploading.value = false
  }
}

// コース一覧読み込み
const loadCourses = async () => {
  try {
    const data = await apiCall('/api/courses')
    courses.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Failed to load courses:', error)
    alert('コース読み込みエラー')
  }
}

// ステータス読み込み
const loadStatus = async () => {
  try {
    const data = await apiCall('/api/status')
    currentStatus.value = data?.status || '未設定'
  } catch (error) {
    console.error('Failed to load status:', error)
    currentStatus.value = '未設定'
  }
}

// コメント読み込み
const loadComments = async () => {
  try {
    const data = await apiCall('/api/comments/with_students')
    comments.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Failed to load comments:', error)
    alert('コメント読み込みエラー')
  }
}

// 今日のコース情報読み込み
const loadTodayInfo = async () => {
  try {
    const data = await apiCall('/api/class_course')
    todayInfo.value = data?.course_id 
      ? `✅ 今日のコース: ${data.course_id}` 
      : '❌ 今日のコースは未設定です'
  } catch (error) {
    console.error('Failed to load today info:', error)
    todayInfo.value = '❌ 今日のコースは未設定です'
  }
}

// 今日のコース設定
const setTodayCourse = async () => {
  if (!selectedTodayCourse.value) {
    alert('コースを選択してください')
    return
  }
  
  try {
    await apiCall('/api/class_course/set', {
      method: 'POST',
      body: JSON.stringify({ course_id: selectedTodayCourse.value })
    })
    alert('✅ 設定完了')
    await loadTodayInfo()
  } catch (error) {
    console.error('Failed to set today course:', error)
    alert(`❌ 設定失敗: ${error.message}`)
  }
}

// ステータス設定
const setStatus = async () => {
  if (!selectedStatus.value) {
    alert('ステータスを選択してください')
    return
  }
  
  try {
    await apiCall('/api/status', {
      method: 'POST',
      body: JSON.stringify({ status: selectedStatus.value })
    })
    alert('✅ ステータス設定完了')
    await loadStatus()
  } catch (error) {
    console.error('Failed to set status:', error)
    alert(`❌ 設定失敗: ${error.message}`)
  }
}

// コースプレビュー
const previewCourse = async (courseId) => {
  previewCourseId.value = courseId
  previewError.value = ''
  showPreviewModal.value = true
  
  // モーダルが表示されるまで待機
  await nextTick()
  
  try {
    // GPXファイルの内容を取得
    const courseData = await apiCall(`/api/courses/${courseId}`)
    const gpxContent = courseData.gpx || courseData.content || courseData.gpx_content
    
    if (!gpxContent) {
      throw new Error('GPXデータが見つかりません')
    }
    
    // 既存の地図があれば破棄
    if (previewMap.value) {
      previewMap.value.remove()
      previewMap.value = null
    }
    
    // DOM要素が完全に準備されるまで少し待機
    await new Promise(resolve => setTimeout(resolve, 100))
    
    if (!previewMapContainer.value) {
      throw new Error('地図コンテナが見つかりません')
    }
    
    // 地図コンテナをクリア
    previewMapContainer.value.innerHTML = ''
    
    // 地図を初期化（オプションを明示的に指定）
    previewMap.value = L.map(previewMapContainer.value, {
      center: [35.6812, 139.7671], // デフォルト位置（東京）
      zoom: 10,
      zoomControl: true,
      attributionControl: true
    })
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(previewMap.value)
    
    // 地図のサイズを強制的に再計算
    setTimeout(() => {
      if (previewMap.value) {
        previewMap.value.invalidateSize()
      }
    }, 100)
    
    // GPXデータを解析
    const parser = new DOMParser()
    const gpxDoc = parser.parseFromString(gpxContent, 'text/xml')
    const trackPoints = gpxDoc.querySelectorAll('trkpt')
    
    if (trackPoints.length === 0) {
      throw new Error('GPXファイルにトラックポイントが見つかりません')
    }
    
    // 座標をLatLngオブジェクトの配列に変換
    const coordinates = []
    trackPoints.forEach(point => {
      const lat = parseFloat(point.getAttribute('lat'))
      const lng = parseFloat(point.getAttribute('lon'))
      coordinates.push([lat, lng])
    })
    
    // ルートをラインとして地図に表示
    const routeLine = L.polyline(coordinates, {
      color: 'red',
      weight: 3,
      opacity: 0.8
    }).addTo(previewMap.value)
    
    // 地図の表示範囲をルート全体に合わせる
    previewMap.value.fitBounds(routeLine.getBounds(), { padding: [20, 20] })
    
    // スタートとゴールにマーカーを追加
    if (coordinates.length > 0) {
      L.marker(coordinates[0])
        .addTo(previewMap.value)
        .bindPopup('スタート')
      
      if (coordinates.length > 1) {
        L.marker(coordinates[coordinates.length - 1])
          .addTo(previewMap.value)
          .bindPopup('ゴール')
      }
    }
    
  } catch (error) {
    console.error('Preview failed:', error)
    previewError.value = error.message
  }
}

// プレビューモーダルを閉じる
const closePreviewModal = () => {
  showPreviewModal.value = false
  previewError.value = ''
  
  if (previewMap.value) {
    previewMap.value.remove()
    previewMap.value = null
  }
}

// 全更新
const refreshAll = async () => {
  await Promise.all([
    loadCourses(),
    loadStatus(),
    loadComments(),
    loadTodayInfo()
  ])
}

// 定期更新
let updateInterval = null

onMounted(async () => {
  console.log('先生用ダッシュボードが開始されました')
  await refreshAll()
  
  // 30秒ごとに更新
  updateInterval = setInterval(() => {
    loadComments()
    loadStatus()
  }, 30000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  
  if (previewMap.value) {
    previewMap.value.remove()
    previewMap.value = null
  }
})
</script>

<style scoped>
.teacher-screen {
  min-height: auto;
  background: #f5f5f5;
  padding: 20px 0 40px;
  overflow: visible;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px 0;
}

.h1 {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.col {
  flex: 1;
}

.input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn {
  padding: 8px 16px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn:hover:not(:disabled) {
  background: #1565c0;
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

.list {
  min-height: 60px;
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px;
}

.empty-state {
  color: #999;
  font-size: 14px;
  padding: 12px;
  text-align: center;
}

.course-item {
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-id {
  font-weight: 500;
  color: #1976d2;
}

.course-meta {
  font-size: 12px;
  color: #999;
}

.course-item-actions {
  display: flex;
  gap: 8px;
}

.comment-item {
  padding: 12px;
  border-left: 3px solid #1976d2;
  background: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 8px;
}

.comment-meta {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.info-box {
  padding: 12px;
  background: #e3f2fd;
  border-radius: 6px;
  color: #1565c0;
}

.course-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.course-modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.course-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.course-modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.preview-map {
  width: 100%;
  height: 400px;
  border-radius: 8px;
  flex: 1;
}

.error-message {
  padding: 20px;
  text-align: center;
  color: #e74c3c;
  background: #ffeaea;
  border-radius: 4px;
  margin-top: 10px;
}

@media (max-width: 768px) {
  .container {
    padding: 0 10px;
  }
  
  .header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .h1 {
    font-size: 24px;
  }
  
  .row {
    flex-direction: column;
  }
  
  .course-modal-content {
    width: 95%;
    padding: 15px;
  }
  
  .preview-map {
    height: 300px;
  }
}
</style>