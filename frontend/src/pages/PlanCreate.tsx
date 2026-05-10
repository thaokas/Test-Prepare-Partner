import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { agentApi, planApi } from '@/api'
import type { FoundationLevel } from '@/types'
import { processAgentTurn, confirmAndGenerate, toggleSearchResult } from '@/agents/planGenerator'
import { createInitialState, GREETING_MESSAGE } from '@/agents/types'
import type { AgentState, SearchResultItem } from '@/agents/types'
import dayjs from 'dayjs'

interface ChatMessage {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  time: string
  planId?: string
  planName?: string
}

let msgIdCounter = 1

export default function PlanCreate() {
  const navigate = useNavigate()
  const [agentState, setAgentState] = useState<AgentState>(createInitialState())
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: msgIdCounter++,
      role: 'assistant',
      content: GREETING_MESSAGE,
      time: dayjs().format('HH:mm'),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [planGenerated, setPlanGenerated] = useState(false)
  const [generating, setGenerating] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const showSearchCard =
    agentState.searchResults.length > 0 &&
    agentState.stage !== 'complete' &&
    !planGenerated

  const showConfirmCard =
    agentState.stage === 'confirm' && !planGenerated

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (msg: Omit<ChatMessage, 'id' | 'time'>) => {
    setMessages((prev) => [
      ...prev,
      { ...msg, id: msgIdCounter++, time: dayjs().format('HH:mm') },
    ])
  }

  const persistPlan = async (state: AgentState): Promise<AgentState> => {
    const profile = state.profile
    const tasks = state.tasks!
    try {
      const planRes = await planApi.createWithTasks({
        examName: profile.exam_name!,
        examType: profile.exam_type!,
        examDate: profile.exam_date!,
        dailyHours: profile.daily_hours || 2,
        foundationLevel: (profile.foundation_level ?? 1) as FoundationLevel,
        weakSubjects: profile.weak_subjects,
        currentMode: 0,
        tasks,
      })
      const plan = planRes.data.data
      return { ...state, planId: plan.planId }
    } catch {
      throw new Error('plan_save_failed')
    }
  }

  const handleSend = async (text?: string) => {
    const msg = (text ?? input.trim())
    if (!msg || loading || planGenerated) return

    addMessage({ role: 'user', content: msg })
    if (!text) setInput('')
    setLoading(true)

    try {
      const result = await processAgentTurn(
        msg,
        agentState,
        async (msgs, sysPrompt) => {
          const res = await agentApi.llmChat({ messages: msgs, system_prompt: sysPrompt })
          const data = res.data.data
          if (data.error) {
            throw new Error(`LLM服务异常: ${data.error}`)
          }
          if (!data.content) {
            throw new Error('LLM返回空内容，请检查Agent服务日志')
          }
          return data.content
        },
        async (query) => {
          const res = await agentApi.search({ query })
          const results = res.data.data.results || []
          return results.map((r) => `[${r.title}] ${r.snippet} (${r.url})`)
        },
      )

      let newState = result.updatedState

      // If plan was generated (stage complete with tasks), persist to backend
      if (newState.stage === 'complete' && newState.tasks && newState.tasks.length > 0) {
        const taskCount = newState.tasks.length
        try {
          newState = await persistPlan(newState)
          setAgentState(newState)
          setPlanGenerated(true)
          addMessage({
            role: 'assistant',
            content: result.assistantMessage,
            planId: newState.planId,
            planName: `已生成 ${taskCount} 个学习任务`,
          })
        } catch {
          addMessage({
            role: 'assistant',
            content: result.assistantMessage + '\n\n⚠️ 计划保存失败，请稍后重试。',
          })
          setAgentState(newState)
        }
      } else {
        setAgentState(newState)
        addMessage({ role: 'assistant', content: result.assistantMessage })
      }
    } catch (err) {
      console.error('Agent调用失败:', err)
      addMessage({
        role: 'assistant',
        content: '抱歉，我暂时无法响应，请稍后再试。',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmGenerate = async () => {
    setGenerating(true)
    try {
      const result = await confirmAndGenerate(
        agentState,
        async (msgs, sysPrompt) => {
          const res = await agentApi.llmChat({ messages: msgs, system_prompt: sysPrompt })
          const data = res.data.data
          if (data.error) {
            throw new Error(`LLM服务异常: ${data.error}`)
          }
          if (!data.content) {
            throw new Error('LLM返回空内容，请检查Agent服务日志')
          }
          return data.content
        },
      )

      let newState = result.updatedState
      addMessage({ role: 'assistant', content: result.assistantMessage })

      if (newState.tasks && newState.tasks.length > 0) {
        try {
          newState = await persistPlan(newState)
          setAgentState(newState)
          setPlanGenerated(true)
          navigate(`/plans/${newState.planId}`, { replace: true })
        } catch {
          addMessage({
            role: 'assistant',
            content: '⚠️ 计划保存失败，请稍后重试。',
          })
          setAgentState(newState)
        }
      }
    } catch (err) {
      console.error('生成计划失败:', err)
      addMessage({
        role: 'assistant',
        content: '抱歉，计划生成失败，请稍后再试。',
      })
    } finally {
      setGenerating(false)
    }
  }

  const handleToggleResult = (index: number) => {
    setAgentState((prev) => toggleSearchResult(prev, index))
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleRestart = () => {
    setAgentState(createInitialState())
    setMessages([
      {
        id: msgIdCounter++,
        role: 'assistant',
        content: '好的，让我们重新开始！请告诉我你想备考什么考试~',
        time: dayjs().format('HH:mm'),
      },
    ])
    setPlanGenerated(false)
  }

  const profile = agentState.profile

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between flex-shrink-0 mb-2">
        <h1 className="text-lg font-bold text-gray-800">创建备考计划</h1>
        {messages.length > 1 && (
          <button
            onClick={handleRestart}
            className="text-xs text-gray-400 hover:text-gray-600 transition"
          >
            重新开始
          </button>
        )}
      </div>

      {/* Profile status bar */}
      {profile.exam_name && !planGenerated && (
        <div className="flex-shrink-0 mb-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-xl">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-blue-500 font-medium">已收集：</span>
            {profile.exam_name && (
              <span className="text-xs bg-white text-blue-700 px-2 py-0.5 rounded-full border border-blue-200">
                {profile.exam_name}{profile.exam_type ? `（${profile.exam_type}）` : ''}
              </span>
            )}
            {profile.exam_date && (
              <span className="text-xs bg-white text-blue-700 px-2 py-0.5 rounded-full border border-blue-200">
                考试：{profile.exam_date}
              </span>
            )}
            {profile.daily_hours != null && (
              <span className="text-xs bg-white text-blue-700 px-2 py-0.5 rounded-full border border-blue-200">
                每天{profile.daily_hours}h
              </span>
            )}
            {profile.foundation_level != null && (
              <span className="text-xs bg-white text-blue-700 px-2 py-0.5 rounded-full border border-blue-200">
                基础：{['零基础', '有一定基础', '基础较好'][profile.foundation_level] ?? '未知'}
              </span>
            )}
            {profile.weak_subjects.length > 0 && (
              <span className="text-xs bg-white text-blue-700 px-2 py-0.5 rounded-full border border-blue-200">
                薄弱：{profile.weak_subjects.join('、')}
              </span>
            )}
            {profile.missing_fields.length > 0 && (
              <span className="text-xs text-amber-500 ml-1">
                还需：{profile.missing_fields.join('、')}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 py-2">
        {messages.map((msg) => (
          <div key={msg.id}>
            <div
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[82%] ${
                  msg.role === 'user' ? 'items-end' : 'items-start'
                } flex flex-col gap-1`}
              >
                {msg.role === 'assistant' && (
                  <span className="text-xs text-gray-400 px-1"><img src="/logo.png" alt="小搭" className="w-5 h-5 inline-block align-middle" /> 小搭</span>
                )}
                <div
                  className={`px-4 py-3 rounded-2xl text-sm ${
                    msg.role === 'user'
                      ? 'bg-blue-500 text-white rounded-br-sm'
                      : 'bg-white text-gray-700 shadow-sm border border-gray-100 rounded-bl-sm'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <div className="prose prose-sm max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-li:text-gray-700 prose-strong:text-gray-800 prose-a:text-blue-500">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  ) : (
                    <span className="whitespace-pre-wrap">{msg.content}</span>
                  )}
                </div>
                <span className="text-xs text-gray-300 px-1">{msg.time}</span>
              </div>
            </div>

            {/* Plan generated card */}
            {msg.planId && planGenerated && (
              <div className="flex justify-start mt-2">
                <div className="bg-green-50 border border-green-300 rounded-2xl p-4 max-w-[85%] w-full">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-3xl">📋</span>
                    <div>
                      <p className="font-semibold text-green-800">
                        {msg.planName ?? '备考计划'}
                      </p>
                      <p className="text-xs text-green-600">AI 已为你量身定制</p>
                    </div>
                  </div>
                  <button
                    onClick={() => navigate(`/plans/${msg.planId}`)}
                    className="w-full bg-green-500 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-green-600 transition active:scale-[0.98]"
                  >
                    查看计划详情 →
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-100 shadow-sm text-gray-400 text-sm px-4 py-3 rounded-2xl rounded-bl-sm">
              <div className="flex items-center gap-2">
                <span className="text-xs">AI 正在思考</span>
                <span className="inline-flex gap-1">
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce" />
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:0.15s]" />
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:0.3s]" />
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Search results card */}
        {showSearchCard && (
          <SearchResultsCard
            results={agentState.searchResults}
            onToggle={handleToggleResult}
          />
        )}

        {/* Confirmation card */}
        {showConfirmCard && (
          <ConfirmCard
            profile={profile}
            onConfirm={handleConfirmGenerate}
            loading={generating}
          />
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      {!planGenerated && (
        <div className="flex-shrink-0 flex gap-2 pt-3 border-t border-gray-100">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入你的备考需求..."
            rows={1}
            disabled={loading}
            className="flex-1 px-4 py-3 border border-gray-200 rounded-2xl text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 transition disabled:bg-gray-50"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="w-12 h-12 bg-blue-500 disabled:bg-blue-300 text-white rounded-2xl flex items-center justify-center hover:bg-blue-600 transition flex-shrink-0 active:scale-95"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
      )}

      {/* Restart button when plan is done */}
      {planGenerated && (
        <div className="flex-shrink-0 pt-3 border-t border-gray-100">
          <button
            onClick={handleRestart}
            className="w-full border-2 border-dashed border-gray-300 text-gray-400 py-3 rounded-2xl text-sm hover:border-blue-300 hover:text-blue-400 transition"
          >
            + 创建新的备考计划
          </button>
        </div>
      )}
    </div>
  )
}

/** Search results card with relevance toggles */
function SearchResultsCard({
  results,
  onToggle,
}: {
  results: SearchResultItem[]
  onToggle: (index: number) => void
}) {
  const [collapsed, setCollapsed] = useState(false)

  if (results.length === 0) return null

  return (
    <div className="flex justify-start">
      <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 max-w-[88%] w-full">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">🔍</span>
            <span className="text-sm font-semibold text-amber-800">
              搜索到的备考资料 ({results.length} 条)
            </span>
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="text-xs text-amber-500 hover:text-amber-700 transition"
          >
            {collapsed ? '展开' : '收起'}
          </button>
        </div>
        <p className="text-xs text-amber-600 mb-3">
          以下资料将辅助计划生成。你可以点击切换按钮标记不需要的资料，生成计划时会自动排除。
        </p>
        {!collapsed && (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {results.map((r, i) => (
              <div
                key={i}
                className={`flex items-start gap-2 p-2 rounded-lg text-xs transition ${
                  r.relevant
                    ? 'bg-white border border-amber-100'
                    : 'bg-gray-100 border border-gray-200 opacity-50'
                }`}
              >
                <button
                  onClick={() => onToggle(i)}
                  className={`flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5 transition ${
                    r.relevant
                      ? 'border-green-400 bg-green-400 text-white'
                      : 'border-gray-300 bg-white text-gray-300'
                  }`}
                  title={r.relevant ? '点击排除' : '点击恢复'}
                >
                  {r.relevant ? '✓' : '✕'}
                </button>
                <div className="flex-1 min-w-0">
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`font-medium hover:underline ${
                      r.relevant ? 'text-blue-600' : 'text-gray-400'
                    }`}
                  >
                    {r.title || '无标题'}
                  </a>
                  <p className={`mt-0.5 line-clamp-2 ${r.relevant ? 'text-gray-600' : 'text-gray-400'}`}>
                    {r.snippet}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/** Confirmation card with profile summary and generate button */
function ConfirmCard({
  profile,
  onConfirm,
  loading,
}: {
  profile: AgentState['profile']
  onConfirm: () => void
  loading: boolean
}) {
  const examDate = profile.exam_date
  const daysUntilExam = examDate
    ? dayjs(examDate).diff(dayjs(), 'day')
    : null

  return (
    <div className="flex justify-start">
      <div className="bg-green-50 border border-green-300 rounded-2xl p-4 max-w-[88%] w-full">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl">✅</span>
          <span className="text-sm font-semibold text-green-800">信息确认</span>
        </div>

        <div className="bg-white border border-green-100 rounded-xl p-3 mb-3 space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-500">考试名称</span>
            <span className="text-gray-800 font-medium">
              {profile.exam_name}{profile.exam_type ? `（${profile.exam_type}）` : ''}
            </span>
          </div>
          {profile.exam_date && (
            <div className="flex justify-between">
              <span className="text-gray-500">考试日期</span>
              <span className="text-gray-800 font-medium">
                {profile.exam_date}
                {daysUntilExam != null && (
                  <span className="text-green-600 ml-1">（距考试还有 {daysUntilExam} 天）</span>
                )}
              </span>
            </div>
          )}
          {profile.daily_hours != null && (
            <div className="flex justify-between">
              <span className="text-gray-500">每日学习时间</span>
              <span className="text-gray-800 font-medium">{profile.daily_hours} 小时</span>
            </div>
          )}
          {profile.foundation_level != null && (
            <div className="flex justify-between">
              <span className="text-gray-500">基础水平</span>
              <span className="text-gray-800 font-medium">
                {['零基础', '有一定基础', '基础较好'][profile.foundation_level]}
              </span>
            </div>
          )}
          {profile.weak_subjects.length > 0 && (
            <div className="flex justify-between">
              <span className="text-gray-500">薄弱科目</span>
              <span className="text-gray-800 font-medium">{profile.weak_subjects.join('、')}</span>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-gray-500">每周休息</span>
            <span className="text-gray-800 font-medium">{profile.rest_days_per_week} 天</span>
          </div>
        </div>

        <button
          onClick={onConfirm}
          disabled={loading}
          className="w-full bg-green-500 disabled:bg-green-300 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-green-600 transition active:scale-[0.98] flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <span className="inline-flex gap-1">
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" />
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce [animation-delay:0.15s]" />
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce [animation-delay:0.3s]" />
              </span>
              <span>正在生成专属备考计划...</span>
            </>
          ) : (
            '确认无误，生成备考计划 →'
          )}
        </button>
        <p className="text-xs text-gray-400 mt-2 text-center">
          如需修改，请在下方输入框中说明需要调整的内容
        </p>
      </div>
    </div>
  )
}
