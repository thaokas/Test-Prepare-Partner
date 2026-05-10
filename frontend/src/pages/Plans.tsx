import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { planApi } from '@/api'
import { useAuthStore } from '@/store/authStore'
import type { PlanResponse } from '@/types'
import { PLAN_STATUS_LABELS, SUPERVISION_MODE_LABELS } from '@/types'
import ProgressBar from '@/components/ProgressBar'
import Loading from '@/components/Loading'
import Empty from '@/components/Empty'
import dayjs from 'dayjs'

export default function Plans() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [plans, setPlans] = useState<PlanResponse[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const userId = user?.userId ?? localStorage.getItem('userId')
    if (!userId) return
    planApi.getByUser(userId)
      .then((res) => setPlans(res.data.data))
      .finally(() => setLoading(false))
  }, [user])

  const handleDelete = async (planId: string) => {
    if (!confirm('确定要删除这个计划吗？')) return
    try {
      await planApi.deletePlan(planId)
      setPlans((prev) => prev.filter((p) => p.planId !== planId))
    } catch (e) {
      console.error('删除计划失败:', e)
      alert('删除失败，请稍后重试')
    }
  }

  if (loading) return <Loading />

  return (
    <div className="space-y-4 pb-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-800">我的备考计划</h2>
        <button
          onClick={() => navigate('/plans/create')}
          className="bg-blue-500 text-white text-sm px-4 py-2 rounded-xl hover:bg-blue-600 transition"
        >
          + 新建
        </button>
      </div>

      {plans.length === 0 ? (
        <Empty text="还没有备考计划，快去创建吧~" />
      ) : (
        plans.map((plan) => (
          <PlanCard
            key={plan.planId}
            plan={plan}
            onView={() => navigate(`/plans/${plan.planId}`)}
            onDelete={() => handleDelete(plan.planId)}
          />
        ))
      )}
    </div>
  )
}

function PlanCard({
  plan,
  onView,
  onDelete,
}: {
  plan: PlanResponse
  onView: () => void
  onDelete: () => void
}) {
  const daysLeft = dayjs(plan.examDate).diff(dayjs(), 'day')
  const statusColor: Record<number, string> = {
    0: 'bg-green-50 text-green-600 border-green-100',
    1: 'bg-gray-50 text-gray-500 border-gray-100',
    2: 'bg-yellow-50 text-yellow-600 border-yellow-100',
  }

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-gray-800">{plan.examName}</h3>
          <p className="text-xs text-gray-400 mt-0.5">{plan.examType}</p>
        </div>
        <span className={`text-xs border px-2 py-1 rounded-full ${statusColor[plan.planStatus]}`}>
          {PLAN_STATUS_LABELS[plan.planStatus]}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className="bg-gray-50 rounded-xl py-2">
          <p className="text-lg font-bold text-blue-500">{daysLeft > 0 ? daysLeft : 0}</p>
          <p className="text-xs text-gray-400">剩余天数</p>
        </div>
        <div className="bg-gray-50 rounded-xl py-2">
          <p className="text-lg font-bold text-green-500">{plan.completedTasks}</p>
          <p className="text-xs text-gray-400">已完成</p>
        </div>
        <div className="bg-gray-50 rounded-xl py-2">
          <p className="text-lg font-bold text-gray-600">{plan.dailyHours}h</p>
          <p className="text-xs text-gray-400">每日目标</p>
        </div>
      </div>

      <ProgressBar value={plan.completedTasks} max={plan.totalTasks} showLabel />

      <div className="flex items-center justify-between mt-3">
        <span className="text-xs text-gray-400">{SUPERVISION_MODE_LABELS[plan.currentMode]}</span>
        <div className="flex gap-2">
          <button
            onClick={onDelete}
            className="text-xs text-red-400 hover:text-red-600 transition"
          >
            删除
          </button>
          <button
            onClick={onView}
            className="text-xs bg-blue-500 text-white px-3 py-1.5 rounded-lg hover:bg-blue-600 transition"
          >
            查看详情
          </button>
        </div>
      </div>
    </div>
  )
}
