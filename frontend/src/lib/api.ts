import axios from 'axios'

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export const api = axios.create({ baseURL: API_URL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('repopilot_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
