// API 設定
export const API_CONFIG = {
  // 本番環境では環境変数やビルド時設定で上書き可能
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  
  // APIエンドポイントのフルURL を取得する関数
  getApiUrl: (path) => {
    // パスが既にフルURLの場合はそのまま返す
    if (path.startsWith('http')) {
      return path
    }
    // 相対パスの場合はベースURLと結合
    return `${API_CONFIG.baseURL}${path}`
  }
}

// デバッグ用
console.log('API Config:', {
  baseURL: API_CONFIG.baseURL,
  environment: import.meta.env.MODE
})