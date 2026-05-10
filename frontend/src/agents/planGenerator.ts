import dayjs from 'dayjs'
import type { AgentStage, AgentState, AgentTurnResult, AgentUIAction, LlmJsonOutput, GeneratedTask, SearchResultItem } from './types'
import {
  EXTRACT_INTENT_PROMPT,
  ASK_MISSING_PROMPT,
  CONFIRM_PROMPT,
  GENERATE_PLAN_PROMPT,
} from './prompts'
import type { ChatMessageItem, ProfileSummary } from '@/types'

type LlmChatFn = (messages: ChatMessageItem[], systemPrompt: string) => Promise<string>
type SearchFn = (query: string) => Promise<string[]>

const REQUIRED_FIELDS: (keyof ProfileSummary)[] = [
  'exam_name',
  'exam_type',
  'exam_date',
  'daily_hours',
]

function parseLlmJson(text: string): LlmJsonOutput {
  try {
    return JSON.parse(text)
  } catch {
    /* try next strategy */
  }

  const codeBlock = text.match(/```(?:json)?\s*([\s\S]*?)```/)
  if (codeBlock) {
    try {
      return JSON.parse(codeBlock[1].trim())
    } catch {
      /* try next strategy */
    }
  }

  const braceMatch = text.match(/\{[\s\S]*\}/)
  if (braceMatch) {
    try {
      return JSON.parse(braceMatch[0])
    } catch {
      /* fall through */
    }
  }

  return { message: text }
}

function computeMissingFields(profile: ProfileSummary): string[] {
  const missing: string[] = []
  for (const field of REQUIRED_FIELDS) {
    const val = profile[field]
    if (val == null || val === '') {
      const labels: Record<string, string> = {
        exam_name: '考试名称',
        exam_type: '考试类型（如：考研、考证、语言、期末等）',
        exam_date: '考试日期',
        daily_hours: '每日学习时长',
      }
      missing.push(labels[field] || field)
    }
  }
  return missing
}

function mergeProfile(profile: ProfileSummary, extracted: Record<string, unknown>): ProfileSummary {
  const next = { ...profile }
  if (extracted.exam_name) next.exam_name = extracted.exam_name as string
  if (extracted.exam_type) next.exam_type = extracted.exam_type as string
  if (extracted.exam_date) next.exam_date = extracted.exam_date as string
  if (extracted.daily_hours != null) next.daily_hours = extracted.daily_hours as number
  if (extracted.foundation_level != null) next.foundation_level = extracted.foundation_level as number
  if (Array.isArray(extracted.weak_subjects) && extracted.weak_subjects.length > 0) {
    next.weak_subjects = extracted.weak_subjects as string[]
  }
  next.missing_fields = computeMissingFields(next)
  return next
}

function determineStage(state: AgentState): AgentStage {
  const { profile, searchResults } = state

  if (state.stage === 'complete') return 'complete'

  if (!profile.exam_name) return 'extract_intent'

  if (searchResults.length === 0 && state.stage !== 'generate') return 'search'

  if (profile.missing_fields.length > 0) return 'ask_missing'

  if (!profile.is_ready) return 'confirm'

  if (profile.is_ready && !state.tasks) return 'generate'

  return 'complete'
}

async function buildSearchQuery(profile: ProfileSummary): Promise<string> {
  const parts = [profile.exam_name]
  if (profile.exam_type) parts.push(profile.exam_type as string)
  parts.push('考试科目 考试时间 备考建议 学习计划 推荐资料')
  return parts.filter(Boolean).join(' ')
}

function searchResultsToItems(rawResults: string[]): SearchResultItem[] {
  return rawResults.map((r) => {
    const match = r.match(/^\[(.+?)\]\s*(.+?)\s*\((.+?)\)$/)
    if (match) {
      return { title: match[1], snippet: match[2], url: match[3], relevant: true }
    }
    return { title: '', snippet: r, url: '', relevant: true }
  })
}

function getRelevantSearchText(results: SearchResultItem[]): string {
  const relevant = results.filter((r) => r.relevant)
  if (relevant.length === 0) return '暂无考试相关信息，请根据考试通用备考经验生成计划。'
  return relevant.map((r) => `[${r.title}] ${r.snippet} (${r.url})`).join('\n')
}

function computeUiAction(state: AgentState, didSearch: boolean): AgentUIAction {
  if (state.stage === 'complete') return 'show_plan_card'
  if (state.stage === 'confirm') return 'show_confirm'
  if (didSearch && state.searchResults.length > 0) return 'show_search_results'
  return 'none'
}

async function handleExtractIntent(
  userMessage: string,
  state: AgentState,
  llmChat: LlmChatFn,
  _search: SearchFn,
): Promise<AgentTurnResult> {
  const llmResult = await llmChat(
    [{ role: 'user', content: userMessage }],
    EXTRACT_INTENT_PROMPT,
  )
  const parsed = parseLlmJson(llmResult)

  state = {
    ...state,
    profile: mergeProfile(state.profile, parsed.extracted || {}),
  }

  let didSearch = false
  if (state.profile.exam_name && state.searchResults.length === 0) {
    const query = await buildSearchQuery(state.profile)
    const rawResults = await _search(query)
    state = { ...state, searchResults: searchResultsToItems(rawResults) }
    didSearch = true
  }

  const nextStage = determineStage(state)
  state = { ...state, stage: nextStage }

  if (didSearch && state.profile.missing_fields.length > 0) {
    const searchSummary = state.searchResults.slice(0, 3).map((r) => r.snippet).join('\n')
    const followUpSystemPrompt = `你收集了用户想备考"${state.profile.exam_name}"的信息。搜索结果：${searchSummary || '暂无'}。请友好地告诉用户你已搜索到相关信息（展示在下方卡片中），然后自然地询问第一个缺失信息：${state.profile.missing_fields[0]}。只输出你的对话文本，不要JSON。`
    const followUp = await llmChat(
      [{ role: 'user', content: '请根据系统提示生成回复' }],
      followUpSystemPrompt,
    )
    return { assistantMessage: followUp, updatedState: state, didSearch, uiAction: computeUiAction(state, didSearch) }
  }

  return {
    assistantMessage: parsed.message || '收到！让我来帮你规划备考计划。',
    updatedState: state,
    didSearch,
    uiAction: computeUiAction(state, didSearch),
  }
}

async function handleAskMissing(
  userMessage: string,
  state: AgentState,
  llmChat: LlmChatFn,
): Promise<AgentTurnResult> {
  const searchSummary = state.searchResults.length > 0
    ? state.searchResults.slice(0, 5).map((r) => r.snippet).join('\n')
    : '暂无搜索结果'

  const prompt = ASK_MISSING_PROMPT
    .replace('{profile_json}', JSON.stringify(state.profile, null, 2))
    .replace('{search_summary}', searchSummary)
    .replace('{missing_fields}', state.profile.missing_fields.join('、'))

  const llmResult = await llmChat(
    [{ role: 'user', content: userMessage }],
    prompt,
  )
  const parsed = parseLlmJson(llmResult)

  state = {
    ...state,
    profile: mergeProfile(state.profile, parsed.extracted || {}),
  }

  const nextStage = determineStage(state)
  state = { ...state, stage: nextStage }

  return {
    assistantMessage: parsed.message || '明白了！还有其他信息需要补充吗？',
    updatedState: state,
    didSearch: false,
    uiAction: computeUiAction(state, false),
  }
}

async function handleConfirm(
  userMessage: string,
  state: AgentState,
  llmChat: LlmChatFn,
): Promise<AgentTurnResult> {
  const searchSummary = state.searchResults.length > 0
    ? state.searchResults.filter((r) => r.relevant).slice(0, 5).map((r) => r.snippet).join('\n')
    : '暂无'
  const todayDate = dayjs().format('YYYY年MM月DD日')

  const prompt = CONFIRM_PROMPT
    .replace('{profile_json}', JSON.stringify(state.profile, null, 2))
    .replace('{search_summary}', searchSummary)
    .replace('{today_date}', todayDate)

  const llmResult = await llmChat(
    [{ role: 'user', content: userMessage }],
    prompt,
  )
  const parsed = parseLlmJson(llmResult)

  if (parsed.extracted) {
    state = {
      ...state,
      profile: mergeProfile(state.profile, parsed.extracted),
    }
  }

  if (parsed.confirmation) {
    state = {
      ...state,
      stage: 'generate',
      profile: { ...state.profile, is_ready: true, missing_fields: [] },
    }
  } else {
    state = {
      ...state,
      stage: 'ask_missing',
      profile: {
        ...state.profile,
        is_ready: false,
        missing_fields: computeMissingFields(state.profile),
      },
    }
  }

  return {
    assistantMessage: parsed.message || '以上是收集到的信息，请确认是否正确？',
    updatedState: state,
    didSearch: false,
    uiAction: computeUiAction(state, false),
  }
}

async function handleGenerate(
  state: AgentState,
  llmChat: LlmChatFn,
): Promise<AgentTurnResult> {
  const todayDate = dayjs().format('YYYY-MM-DD')
  const searchText = getRelevantSearchText(state.searchResults)
  const weakSubjects = state.profile.weak_subjects.length > 0
    ? state.profile.weak_subjects.join('、')
    : '无特别薄弱科目'

  const prompt = GENERATE_PLAN_PROMPT
    .replace('{profile_json}', JSON.stringify(state.profile, null, 2))
    .replace('{search_results_text}', searchText)
    .replace('{today_date}', todayDate)
    .replace('{rest_days_per_week}', String(state.profile.rest_days_per_week))
    .replace('{daily_hours}', String(state.profile.daily_hours || 2))
    .replace('{weak_subjects}', weakSubjects)

  const llmResult = await llmChat([], prompt)
  const parsed = parseLlmJson(llmResult)

  const tasks: GeneratedTask[] = (parsed.plan_tasks || []).map((t) => ({
    taskDate: t.taskDate,
    subject: t.subject || '',
    taskContent: t.taskContent || '',
    estimatedMinutes: t.estimatedMinutes || 60,
    taskType: t.taskType || 1,
    phase: t.phase || 1,
  }))

  state = {
    ...state,
    stage: 'complete',
    tasks,
  }

  return {
    assistantMessage: parsed.message || '🎉 你的专属备考计划已经生成完毕！',
    updatedState: state,
    didSearch: false,
    uiAction: 'show_plan_card',
  }
}

/** Toggle relevance of a search result by index. Returns new state (does not mutate). */
export function toggleSearchResult(state: AgentState, index: number): AgentState {
  if (index < 0 || index >= state.searchResults.length) return state
  const updated = [...state.searchResults]
  updated[index] = { ...updated[index], relevant: !updated[index].relevant }
  return { ...state, searchResults: updated }
}

/** Called when user clicks the confirm button — skips LLM confirm, goes straight to generate. */
export async function confirmAndGenerate(
  state: AgentState,
  llmChatFn: LlmChatFn,
): Promise<AgentTurnResult> {
  const readyState: AgentState = {
    ...state,
    stage: 'generate',
    profile: { ...state.profile, is_ready: true, missing_fields: [] },
  }
  return handleGenerate(readyState, llmChatFn)
}

export async function processAgentTurn(
  userMessage: string,
  currentState: AgentState,
  llmChatFn: LlmChatFn,
  searchFn: SearchFn,
): Promise<AgentTurnResult> {
  let state = { ...currentState }

  const stage = state.stage

  switch (stage) {
    case 'extract_intent':
      return handleExtractIntent(userMessage, state, llmChatFn, searchFn)

    case 'search':
      if (state.searchResults.length === 0 && state.profile.exam_name) {
        const query = await buildSearchQuery(state.profile)
        const rawResults = await searchFn(query)
        state = { ...state, searchResults: searchResultsToItems(rawResults) }
      }
      state = { ...state, stage: 'ask_missing' }
      return handleAskMissing(userMessage, state, llmChatFn)

    case 'ask_missing':
      return handleAskMissing(userMessage, state, llmChatFn)

    case 'confirm':
      return handleConfirm(userMessage, state, llmChatFn)

    case 'generate':
      return handleGenerate(state, llmChatFn)

    case 'complete':
    default:
      return {
        assistantMessage: '计划已生成完毕，如需创建新计划请点击"重新开始"。',
        updatedState: state,
        didSearch: false,
        uiAction: 'none',
      }
  }
}
