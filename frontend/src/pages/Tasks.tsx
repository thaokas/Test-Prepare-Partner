import { useEffect, useState } from 'react'
import { planApi, taskApi } from '@/api'
import { useAuthStore } from '@/store/authStore'
import type { PlanResponse, TaskResponse, TaskStatus } from '@/types'
import { TASK_TYPE_LABELS, TASK_STATUS_LABELS } from '@/types'
import Loading from '@/components/Loading'
import Empty from '@/components/Empty'

export default function Tasks() {
  const user = useAuthStore((s) => s.user)
  const [plans, setPlans] = useState<PlanResponse[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null)
  const [tasks, setTasks] = useState<TaskResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'today' | 'all'>('today')

  useEffect(() => {
    const userId = user?.userId ?? localStorage.getItem('userId')
    if (!userId) return
    planApi.getByUser(userId).then((res) => {
      const activePlans = res.data.data.filter((p) => p.planStatus === 0)
      setPlans(activePlans)
      if (activePlans.length > 0) {
        setSelectedPlanId(activePlans[0].planId)
      } else {
        setLoading(false)
      }
    })
  }, [user])

  useEffect(() => {
    if (!selectedPlanId) return
    setLoading(true)
    const fetch = filter === 'today'
      ? taskApi.getToday(selectedPlanId)
      : taskApi.getByPlan(selectedPlanId)

    fetch.then((res) => setTasks(res.data.data)).finally(() => setLoading(false))
  }, [selectedPlanId, filter])

  const handleComplete = async (taskId: string) => {
    await taskApi.complete(taskId)
    setTasks((prev) => prev.map((t) => t.taskId === taskId ? { ...t, status: 2 as TaskStatus } : t))
  }

  const completedCount = tasks.filter((t) => t.status === 2).length

  return (
    <div className="space-y-4 pb-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-800">今日任务</h2>
        {tasks.length > 0 && (
          <span className="text-sm text-gray-400">{completedCount}/{tasks.length}</span>
        )}
      </div>

      {/* Plan selector */}
      {plans.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {plans.map((plan) => (
            <button
              key={plan.planId}
              onClick={() => setSelectedPlanId(plan.planId)}
              className={`flex-shrink-0 px-3 py-1.5 rounded-xl text-sm border transition ${
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

      {/* Filter toggle */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1">
        <button
          onClick={() => setFilter('today')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${
            filter === 'today' ? 'bg-white text-blue-500 shadow-sm' : 'text-gray-500'
          }`}
        >
          今日任务
        </button>
        <button
          onClick={() => setFilter('all')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${
            filter === 'all' ? 'bg-white text-blue-500 shadow-sm' : 'text-gray-500'
          }`}
        >
          全部任务
        </button>
      </div>

      {loading ? (
        <Loading />
      ) : plans.length === 0 ? (
        <Empty text="暂无进行中的计划" />
      ) : tasks.length === 0 ? (
        <Empty text={filter === 'today' ? '今天没有安排任务，休息一下~' : '暂无任务'} />
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <div
              key={task.taskId}
              className="bg-white rounded-xl p-4 shadow-sm flex items-start gap-3"
            >
              <button
                onClick={() => task.status !== 2 && handleComplete(task.taskId)}
                className={`mt-0.5 w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition ${
                  task.status === 2
                    ? 'bg-green-400 border-green-400 text-white'
                    : 'border-gray-300 hover:border-green-400'
                }`}
              >
                {task.status === 2 && <span className="text-xs">✓</span>}
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <p className={`font-medium text-sm ${task.status === 2 ? 'line-through text-gray-400' : 'text-gray-800'}`}>
                    {task.subject}
                  </p>
                  <span className="text-xs bg-blue-50 text-blue-400 px-1.5 py-0.5 rounded-full">
                    {TASK_TYPE_LABELS[task.taskType]}
                  </span>
                </div>
                <p className="text-xs text-gray-500">{task.taskContent}</p>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-xs text-gray-400">⏱ {task.estimatedMinutes}分钟</span>
                  <span className={`text-xs ${
                    task.status === 2 ? 'text-green-500' :
                    task.status === 1 ? 'text-yellow-500' : 'text-gray-400'
                  }`}>
                    {TASK_STATUS_LABELS[task.status]}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
