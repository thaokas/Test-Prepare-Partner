import type { ProfileSummary } from '@/types'

export type AgentStage =
  | 'extract_intent'
  | 'search'
  | 'ask_missing'
  | 'confirm'
  | 'generate'
  | 'complete'

/** Hint to the UI about what card/action to show after this turn */
export type AgentUIAction = 'none' | 'show_search_results' | 'show_confirm' | 'show_plan_card'

export interface SearchResultItem {
  title: string
  snippet: string
  url: string
  relevant: boolean
}

export interface AgentState {
  stage: AgentStage
  profile: ProfileSummary
  searchResults: SearchResultItem[]
  planId?: string
  tasks?: GeneratedTask[]
  error?: string
}

export interface GeneratedTask {
  taskDate: string
  subject: string
  taskContent: string
  estimatedMinutes: number
  taskType: number
  phase: number
}

export interface AgentTurnResult {
  assistantMessage: string
  updatedState: AgentState
  didSearch: boolean
  uiAction: AgentUIAction
}

export interface LlmJsonOutput {
  message: string
  extracted?: Partial<{
    exam_name: string
    exam_type: string
    exam_date: string
    daily_hours: number
    foundation_level: number
    weak_subjects: string[]
  }>
  confirmation?: boolean
  plan_tasks?: GeneratedTask[]
}

export function createInitialState(): AgentState {
  return {
    stage: 'extract_intent',
    profile: {
      weak_subjects: [],
      rest_days_per_week: 1,
      missing_fields: [],
      is_ready: false,
    },
    searchResults: [],
  }
}

export const GREETING_MESSAGE =
  '你好！我是你的小搭 🤖\n\n你可以直接告诉我你想备考什么考试，我会帮你搜索相关信息，了解你的情况，然后为你量身定制一份专属备考计划。\n\n比如你可以说：\n• "我想备考2027年考研数学一"\n• "帮我制定雅思A类的备考计划"\n• "我在准备CPA会计科目的考试"'
