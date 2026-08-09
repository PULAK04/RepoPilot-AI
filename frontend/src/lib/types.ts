export type Repository = {
  id: number
  owner: string
  name: string
  url: string
  branch: string
  status: string
  file_count: number
  last_error?: string | null
  created_at: string
  updated_at: string
}

export type Analysis = {
  id: number
  repo_id: number
  kind: 'ask' | 'bug' | 'code_review' | 'architecture' | 'tests' | 'performance'
  question: string
  status: string
  progress: number
  current_step: string
  result_json?: Record<string, any> | null
  error?: string | null
  created_at: string
  updated_at: string
}
