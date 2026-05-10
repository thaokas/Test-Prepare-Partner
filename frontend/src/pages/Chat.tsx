import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { agentApi, planApi } from '@/api'
import { useAuthStore } from '@/store/authStore'
import type { ChatMessageItem, PlanResponse, PlanChatResponse, ProfileSummary } from '@/types'
import dayjs from 'dayjs'

interface ChatMessage {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  generatedPlanId?: string
  generatedPlanName?: string
  time: string
}

type FlowStatus = 'idle' | 'conversing' | 'completed'

let msgIdCounter = 1

export default function Chat() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [plans, setPlans] = useState<PlanResponse[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<string | undefined>()
  const [profile, setProfile] = useState<ProfileSummary | null>(null)
  const [searchResults, setSearchResults] = useState<string[]>([])
  const [flowStatus, setFlowStatus] = useState<FlowStatus>('idle')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: msgIdCounter++,
      role: 'assistant',
      content: '你好！我是小搭 🤖\n你可以直接问我备考相关问题，也可以让我帮你定制专属备考计划。告诉我你想备考什么考试吧~',
      time: dayjs().format('HH:mm'),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const userId = user?.userId ?? localStorage.getItem('userId')
    if (!userId) return
    planApi.getByUser(userId).then((res) => {
      const active = res.data.data.filter((p) => p.planStatus === 0)
      setPlans(active)
    })
  }, [user])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addAssistantMessage = (content: string, extra?: Partial<ChatMessage>) => {
    setMessages((prev) => [
      ...prev,
      {
        id: msgIdCounter++,
        role: 'assistant',
        content,
        time: dayjs().format('HH:mm'),
        ...extra,
      },
    ])
  }

  const buildApiMessages = (msgs: ChatMessage[]): ChatMessageItem[] =>
    msgs
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content }))

  const handleResponse = (res: PlanChatResponse) => {
    if (res.profile) setProfile(res.profile)
    if (res.search_results) setSearchResults(res.search_results)

    if (res.status === 'completed') {
      setFlowStatus('completed')
    } else if (res.status === 'waiting_for_input') {
      setFlowStatus('conversing')
    }

    addAssistantMessage(res.message, {
      generatedPlanId: res.plan_id,
    })

    if (res.status === 'completed' && res.plan_id && res.tasks) {
      const planName = res.tasks.length > 0 ? `已生成 ${res.tasks.length} 个任务` : '计划已生成'
      addAssistantMessage('🎉 你的专属备考计划已经生成完毕！点击下方按钮查看计划详情。', {
        generatedPlanId: res.plan_id,
        generatedPlanName: planName,
      })
    }
  }

  const handleSend = async (clarificationAnswer?: string) => {
    const text = clarificationAnswer ?? input.trim()
    if (!text || loading) return

    const userMsg: ChatMessage = {
      id: msgIdCounter++,
      role: 'user',
      content: text,
      time: dayjs().format('HH:mm'),
    }
    setMessages((prev) => [...prev, userMsg])

    if (!clarificationAnswer) {
      setInput('')
    }
    setLoading(true)

    try {
      // Include all conversation rounds (including current message) in messages array
      const allMessages = [...buildApiMessages(messages), { role: 'user' as const, content: text }]
      const res = await agentApi.planChat({
        message: text,
        profile,
        search_results: searchResults,
        messages: allMessages,
      })
      handleResponse(res.data.data)
    } catch {
      addAssistantMessage('抱歉，我暂时无法响应，请稍后再试。')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const flowSteps = [
    { key: 'conversing', label: '对话中' },
    { key: 'completed', label: '完成' },
  ]
  const currentStepIdx = flowSteps.findIndex((s) => s.key === flowStatus)

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Flow status indicator */}
      {(flowStatus !== 'idle') && (
        <div className="flex items-center gap-1 mb-2 flex-shrink-0">
          {flowSteps.map((step, idx) => (
            <div key={step.key} className="flex items-center gap-1 flex-1">
              <div className={`flex-1 h-1 rounded-full transition ${
                idx <= currentStepIdx ? 'bg-blue-500' : 'bg-gray-200'
              }`} />
              <span className={`text-xs flex-shrink-0 ${
                idx <= currentStepIdx ? 'text-blue-500' : 'text-gray-400'
              }`}>
                {step.label}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Profile status bar — shows collected info during multi-turn conversation */}
      {profile && flowStatus !== 'completed' && (
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

      {/* Plan context */}
      {plans.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-2 flex-shrink-0">
          <span className="text-xs text-gray-400 flex-shrink-0 self-center">背景计划：</span>
          {plans.map((plan) => (
            <button
              key={plan.planId}
              onClick={() => setSelectedPlanId(plan.planId === selectedPlanId ? undefined : plan.planId)}
              className={`flex-shrink-0 px-3 py-1 rounded-xl text-xs border transition ${
                selectedPlanId === plan.planId
                  ? 'bg-blue-500 text-white border-blue-500'
                  : 'bg-white text-gray-600 border-gray-200'
              }`}
            >
              {plan.examName}
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 py-2">
        {messages.map((msg) => (
          <div key={msg.id}>
            <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                <div
                  className={`px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                    msg.role === 'user'
                      ? 'bg-blue-500 text-white rounded-br-sm'
                      : 'bg-white text-gray-700 shadow-sm rounded-bl-sm'
                  }`}
                >
                  {msg.content}
                </div>
                <span className="text-xs text-gray-300 px-1">{msg.time}</span>
              </div>
            </div>

            {/* Generated plan card */}
            {msg.generatedPlanId && flowStatus === 'completed' && (
              <div className="flex justify-start mt-2">
                <div className="bg-green-50 border border-green-300 rounded-2xl p-4 max-w-[85%]">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">📋</span>
                    <div>
                      <p className="font-medium text-green-800 text-sm">
                        {msg.generatedPlanName ?? '备考计划'}
                      </p>
                      <p className="text-xs text-green-600">AI 已为你量身定制</p>
                    </div>
                  </div>
                  <button
                    onClick={() => navigate(`/plans/${msg.generatedPlanId}`)}
                    className="w-full bg-green-500 text-white py-2 rounded-xl text-sm font-medium hover:bg-green-600 transition"
                  >
                    查看计划详情 →
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Thinking indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-400 text-sm px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm">
              <span className="inline-flex gap-1">
                <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce" />
                <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:0.15s]" />
                <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:0.3s]" />
              </span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 flex gap-2 pt-2 border-t border-gray-100">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入你的问题..."
          rows={1}
          className="flex-1 px-4 py-3 border border-gray-200 rounded-2xl text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          className="w-12 h-12 bg-blue-500 disabled:bg-blue-300 text-white rounded-2xl flex items-center justify-center hover:bg-blue-600 transition flex-shrink-0"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </div>
  )
}
