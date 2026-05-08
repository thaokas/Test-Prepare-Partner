import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { agentApi, planApi } from '@/api'
import { useAuthStore } from '@/store/authStore'
import type { PlanResponse, PlanChatResponse } from '@/types'
import dayjs from 'dayjs'

interface ChatMessage {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  clarificationQuestion?: string
  generatedPlanId?: string
  generatedPlanName?: string
  time: string
}

type FlowStatus = 'idle' | 'chatting' | 'asking' | 'generating' | 'completed'

let msgIdCounter = 1

export default function Chat() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [plans, setPlans] = useState<PlanResponse[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<string | undefined>()
  const [threadId, setThreadId] = useState<string | null>(null)
  const [flowStatus, setFlowStatus] = useState<FlowStatus>('idle')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: msgIdCounter++,
      role: 'assistant',
      content: '你好！我是你的备考AI助手 🤖\n你可以直接问我备考相关问题，也可以让我帮你定制专属备考计划。告诉我你想备考什么考试吧~',
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

  const handleResponse = (res: PlanChatResponse) => {
    setThreadId(res.threadId)
    setFlowStatus(res.status)

    addAssistantMessage(res.message, {
      clarificationQuestion: res.clarificationQuestion,
      generatedPlanId: res.planId,
    })

    if (res.status === 'completed' && res.planId && res.tasks) {
      const planName = res.tasks.length > 0 ? `已生成 ${res.tasks.length} 个任务` : '计划已生成'
      addAssistantMessage('🎉 你的专属备考计划已经生成完毕！点击下方按钮查看计划详情。', {
        generatedPlanId: res.planId,
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
      const res = await agentApi.planChat({
        message: text,
        threadId: threadId ?? undefined,
        planId: selectedPlanId,
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
    { key: 'chatting', label: '对话中' },
    { key: 'asking', label: '追问' },
    { key: 'generating', label: '生成中' },
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

            {/* Clarification question card */}
            {msg.clarificationQuestion && (
              <div className="flex justify-start mt-2">
                <div className="max-w-[85%] bg-blue-50 border-2 border-blue-300 rounded-2xl p-4">
                  <p className="text-sm text-blue-700 font-medium mb-2">
                    💡 {msg.clarificationQuestion}
                  </p>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="输入你的回答..."
                      id={`clarify-${msg.id}`}
                      className="flex-1 px-3 py-2 border border-blue-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          const val = (e.target as HTMLInputElement).value.trim()
                          if (val) handleSend(val)
                        }
                      }}
                    />
                    <button
                      onClick={() => {
                        const el = document.getElementById(`clarify-${msg.id}`) as HTMLInputElement
                        const val = el?.value?.trim()
                        if (val) handleSend(val)
                      }}
                      className="bg-blue-500 text-white px-4 py-2 rounded-xl text-sm hover:bg-blue-600 transition flex-shrink-0"
                    >
                      发送
                    </button>
                  </div>
                </div>
              </div>
            )}

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

        {/* Generating indicator */}
        {flowStatus === 'generating' && loading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-400 text-sm px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm">
              <p className="mb-2">AI 正在分析你的需求，生成个性化备考计划...</p>
              <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                <div className="bg-blue-500 h-full rounded-full animate-pulse w-3/4" />
              </div>
            </div>
          </div>
        )}

        {/* Typing indicator for non-generating states */}
        {loading && flowStatus !== 'generating' && (
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
