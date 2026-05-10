import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { planApi, taskApi } from '@/api'
import type { PlanResponse, TaskResponse, SupervisionMode } from '@/types'
import {
  PLAN_STATUS_LABELS,
  SUPERVISION_MODE_LABELS,
  SUPERVISION_MODE_DESC,
  TASK_TYPE_LABELS,
  TASK_STATUS_LABELS,
  PHASE_LABELS,
  FOUNDATION_LABELS,
} from '@/types'
import ProgressBar from '@/components/ProgressBar'
import Loading from '@/components/Loading'
import dayjs from 'dayjs'

export default function PlanDetail() {
  const { planId } = useParams<{ planId: string }>()
  const navigate = useNavigate()
  const [plan, setPlan] = useState<PlanResponse | null>(null)
  const [tasks, setTasks] = useState<TaskResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks'>('overview')
  const [showModeModal, setShowModeModal] = useState(false)

  useEffect(() => {
    if (!planId) return
    setLoading(true)
    setError(null)
    setPlan(null)
    setTasks([])

    let planDone = false
    let tasksDone = false

    planApi.getById(planId)
      .then((res) => {
        setPlan(res.data.data)
      })
      .catch((e) => {
        console.error('加载计划失败:', e)
        setError('计划加载失败，请返回重试')
      })
      .finally(() => {
        planDone = true
        if (tasksDone) setLoading(false)
      })

    taskApi.getByPlan(planId)
      .then((res) => {
        setTasks(res.data.data)
      })
      .catch((e) => {
        console.error('加载任务失败:', e)
      })
      .finally(() => {
        tasksDone = true
        if (planDone) setLoading(false)
      })
  }, [planId])

  const handleSwitchMode = async (mode: SupervisionMode) => {
    if (!plan) return
    const res = await planApi.switchMode(plan.planId, mode)
    setPlan(res.data.data)
    setShowModeModal(false)
  }

  const handleCompleteTask = async (taskId: string) => {
    await taskApi.complete(taskId)
    setTasks((prev) =>
      prev.map((t) => (t.taskId === taskId ? { ...t, status: 2 } : t))
    )
    if (plan) {
      setPlan({ ...plan, completedTasks: plan.completedTasks + 1 })
    }
  }

  if (loading) return <Loading />
  if (error) return (
    <div className="text-center py-16">
      <p className="text-red-400 mb-4">{error}</p>
      <button
        onClick={() => navigate('/plans')}
        className="text-blue-500 text-sm border border-blue-200 px-4 py-2 rounded-lg hover:bg-blue-50"
      >
        返回计划列表
      </button>
    </div>
  )
  if (!plan) return (
    <div className="text-center py-16">
      <p className="text-gray-400 mb-4">计划不存在</p>
      <button
        onClick={() => navigate('/plans')}
        className="text-blue-500 text-sm border border-blue-200 px-4 py-2 rounded-lg hover:bg-blue-50"
      >
        返回计划列表
      </button>
    </div>
  )

  const daysLeft = dayjs(plan.examDate).diff(dayjs(), 'day')
  const tasksByDate = tasks.reduce<Record<string, TaskResponse[]>>((acc, task) => {
    const date = task.taskDate
    if (!acc[date]) acc[date] = []
    acc[date].push(task)
    return acc
  }, {})

  return (
    <div className="pb-4">
      {/* Plan header */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-2xl p-5 mb-4">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold">{plan.examName}</h2>
            <p className="text-blue-100 text-sm mt-0.5">{plan.examType}</p>
          </div>
          <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
            {PLAN_STATUS_LABELS[plan.planStatus]}
          </span>
        </div>
        <div className="grid grid-cols-3 gap-3 mt-4">
          <div className="text-center">
            <p className="text-2xl font-bold">{daysLeft > 0 ? daysLeft : 0}</p>
            <p className="text-blue-100 text-xs">剩余天数</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold">{plan.completedTasks}</p>
            <p className="text-blue-100 text-xs">已完成任务</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold">{Math.round(plan.completionRate * 100)}%</p>
            <p className="text-blue-100 text-xs">完成率</p>
          </div>
        </div>
        <ProgressBar value={plan.completedTasks} max={plan.totalTasks} className="mt-3" />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-4">
        {(['overview', 'tasks'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${
              activeTab === tab ? 'bg-white text-blue-500 shadow-sm' : 'text-gray-500'
            }`}
          >
            {tab === 'overview' ? '计划概览' : '任务列表'}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-3">
          <InfoCard label="考试日期" value={dayjs(plan.examDate).format('YYYY年M月D日')} />
          <InfoCard label="每日学习" value={`${plan.dailyHours} 小时`} />
          <InfoCard label="基础水平" value={FOUNDATION_LABELS[plan.foundationLevel]} />
          <InfoCard label="当前阶段" value={PHASE_LABELS[plan.currentPhase]} />
          <InfoCard
            label="薄弱科目"
            value={plan.weakSubjects?.length ? plan.weakSubjects.join('、') : '暂未设置'}
          />
          <div className="bg-white rounded-2xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">督促模式</p>
                <p className="font-medium text-gray-800 mt-0.5">{SUPERVISION_MODE_LABELS[plan.currentMode]}</p>
                <p className="text-xs text-gray-400 mt-0.5">{SUPERVISION_MODE_DESC[plan.currentMode]}</p>
              </div>
              <button
                onClick={() => setShowModeModal(true)}
                className="text-sm text-blue-500 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-50 transition"
              >
                切换
              </button>
            </div>
          </div>
          <button
            onClick={async () => {
              if (confirm('确定要删除这个计划吗？')) {
                try {
                  await planApi.deletePlan(plan.planId)
                  navigate('/plans')
                } catch (e) {
                  console.error('删除计划失败:', e)
                  alert('删除失败，请稍后重试')
                }
              }
            }}
            className="w-full border border-red-200 text-red-400 py-2.5 rounded-xl text-sm hover:bg-red-50 transition"
          >
            删除计划
          </button>
        </div>
      )}

      {activeTab === 'tasks' && (
        <div className="space-y-4">
          {Object.keys(tasksByDate).sort().map((date) => (
            <div key={date}>
              <p className="text-sm font-medium text-gray-500 mb-2">
                {dayjs(date).format('M月D日')} ({tasksByDate[date].length} 个任务)
              </p>
              <div className="space-y-2">
                {tasksByDate[date].map((task) => (
                  <TaskItem key={task.taskId} task={task} onComplete={handleCompleteTask} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Mode modal */}
      {showModeModal && (
        <div className="fixed inset-0 bg-black/40 flex items-end z-50" onClick={() => setShowModeModal(false)}>
          <div className="bg-white w-full rounded-t-2xl p-5" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-bold text-gray-800 mb-4">切换督促模式</h3>
            <div className="space-y-2">
              {([0, 1, 2, 3] as SupervisionMode[]).map((mode) => (
                <button
                  key={mode}
                  onClick={() => handleSwitchMode(mode)}
                  className={`w-full text-left px-4 py-3 rounded-xl border transition ${
                    plan.currentMode === mode
                      ? 'bg-blue-50 border-blue-400'
                      : 'bg-white border-gray-200 hover:border-blue-200'
                  }`}
                >
                  <span className="font-medium text-sm">{SUPERVISION_MODE_LABELS[mode]}</span>
                  <p className="text-xs text-gray-400">{SUPERVISION_MODE_DESC[mode]}</p>
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowModeModal(false)}
              className="w-full mt-3 py-3 text-gray-500 text-sm"
            >
              取消
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-2xl px-4 py-3 shadow-sm flex items-center justify-between">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="text-sm font-medium text-gray-800">{value}</span>
    </div>
  )
}

function TaskItem({
  task,
  onComplete,
}: {
  task: TaskResponse
  onComplete: (id: string) => void
}) {
  const statusColors: Record<number, string> = {
    0: 'bg-gray-100 text-gray-500',
    1: 'bg-yellow-100 text-yellow-600',
    2: 'bg-green-100 text-green-600',
    3: 'bg-gray-100 text-gray-400',
  }

  return (
    <div className="bg-white rounded-xl p-3 shadow-sm flex items-center gap-3">
      <button
        onClick={() => task.status !== 2 && onComplete(task.taskId)}
        className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition ${
          task.status === 2
            ? 'bg-green-400 border-green-400 text-white'
            : 'border-gray-300 hover:border-green-400'
        }`}
      >
        {task.status === 2 && '✓'}
      </button>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium truncate ${task.status === 2 ? 'line-through text-gray-400' : 'text-gray-700'}`}>
          {task.subject}
        </p>
        <p className="text-xs text-gray-400 truncate">{task.taskContent}</p>
      </div>
      <div className="flex flex-col items-end gap-1 flex-shrink-0">
        <span className="text-xs text-gray-400">{task.estimatedMinutes}分钟</span>
        <span className={`text-xs px-1.5 py-0.5 rounded-full ${statusColors[task.status]}`}>
          {TASK_STATUS_LABELS[task.status]}
        </span>
        <span className="text-xs text-gray-300">{TASK_TYPE_LABELS[task.taskType]}</span>
      </div>
    </div>
  )
}
