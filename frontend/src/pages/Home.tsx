import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { planApi, taskApi, checkinApi, authApi } from '@/api'
import { useAuthStore } from '@/store/authStore'
import type { PlanResponse, TaskResponse } from '@/types'
import { PLAN_STATUS_LABELS, SUPERVISION_MODE_LABELS, TASK_TYPE_LABELS } from '@/types'
import ProgressBar from '@/components/ProgressBar'
import Loading from '@/components/Loading'
import dayjs from 'dayjs'

export default function Home() {
  const navigate = useNavigate()
  const { user, setUser } = useAuthStore()
  const [plans, setPlans] = useState<PlanResponse[]>([])
  const [todayTasks, setTodayTasks] = useState<TaskResponse[]>([])
  const [streak, setStreak] = useState(0)
  const [loading, setLoading] = useState(true)

  const sortedPlans = [...plans].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
  )
  const activePlan = sortedPlans.find((p) => p.planStatus === 0)

  useEffect(() => {
    const init = async () => {
      try {
        if (!user) {
          const meRes = await authApi.me()
          setUser(meRes.data.data)
        }
        const userId = user?.userId ?? localStorage.getItem('userId')
        if (!userId) return

        const [plansRes, streakRes] = await Promise.all([
          planApi.getByUser(userId),
          checkinApi.getStreak(),
        ])
        const fetchedPlans = plansRes.data.data
        setPlans(fetchedPlans)
        setStreak(streakRes.data.data)

        const newest = [...fetchedPlans].sort(
          (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
        )
        const running = newest.find((p) => p.planStatus === 0)
        if (running) {
          const tasksRes = await taskApi.getToday(running.planId)
          setTodayTasks(tasksRes.data.data)
        }
      } catch (_) {
        // noop
      } finally {
        setLoading(false)
      }
    }
    init()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const completedToday = todayTasks.filter((t) => t.status === 2).length

  if (loading) return <Loading />

  return (
    <div className="space-y-4 pb-4">
      {/* Header greeting */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-2xl p-5 flex items-center justify-between">
        <div>
          <p className="text-blue-100 text-sm">你好，{user?.nickname ?? '同学'} 👋</p>
          <h2 className="text-xl font-bold mt-1">
            {dayjs().format('M月D日')} {getGreeting()}
          </h2>
          <div className="flex items-center gap-4 mt-3">
            <div className="text-center">
              <p className="text-2xl font-bold">{streak}</p>
              <p className="text-blue-100 text-xs">连续打卡天数</p>
            </div>
            <div className="w-px h-10 bg-blue-300" />
            <div className="text-center">
              <p className="text-2xl font-bold">{user?.totalCheckins ?? 0}</p>
              <p className="text-blue-100 text-xs">累计打卡</p>
            </div>
            <div className="w-px h-10 bg-blue-300" />
            <div className="text-center">
              <p className="text-2xl font-bold">{user?.maxStreak ?? 0}</p>
              <p className="text-blue-100 text-xs">最长连续</p>
            </div>
          </div>
        </div>
        <img src="/logo.png" alt="logo" className="w-24 h-24 rounded-xl flex-shrink-0 ml-4" />
      </div>

      {/* Active plan */}
      {activePlan ? (
        <div className="bg-white rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="font-semibold text-gray-800">{activePlan.examName}</h3>
              <p className="text-xs text-gray-400 mt-0.5">
                {activePlan.examType} · {SUPERVISION_MODE_LABELS[activePlan.currentMode]} ·
                {dayjs(activePlan.examDate).diff(dayjs(), 'day')} 天后考试
              </p>
            </div>
            <span className="text-xs bg-green-50 text-green-600 border border-green-100 px-2 py-1 rounded-full">
              {PLAN_STATUS_LABELS[activePlan.planStatus]}
            </span>
          </div>
          <ProgressBar value={activePlan.completedTasks} max={activePlan.totalTasks} showLabel />
          <div className="flex gap-2 mt-3">
            <button
              onClick={() => navigate(`/plans/${activePlan.planId}`)}
              className="flex-1 text-sm text-blue-500 border border-blue-200 rounded-xl py-2 hover:bg-blue-50 transition"
            >
              查看详情
            </button>
            <button
              onClick={() => navigate('/checkin')}
              className="flex-1 text-sm bg-blue-500 text-white rounded-xl py-2 hover:bg-blue-600 transition"
            >
              去打卡
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-2xl p-5 shadow-sm text-center">
          <p className="text-gray-500 text-sm mb-3">你还没有进行中的备考计划</p>
          <button
            onClick={() => navigate('/plans/create')}
            className="bg-blue-500 text-white px-6 py-2 rounded-xl text-sm hover:bg-blue-600 transition"
          >
            + 创建备考计划
          </button>
        </div>
      )}

      {/* Today's tasks */}
      {activePlan && (
        <div className="bg-white rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800">今日任务</h3>
            {todayTasks.length > 0 && (
              <span className="text-sm text-gray-400">{completedToday}/{todayTasks.length}</span>
            )}
          </div>
          {todayTasks.length > 0 ? (
            <>
              <div className="space-y-2">
                {todayTasks.slice(0, 4).map((task) => (
                  <div
                    key={task.taskId}
                    className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl"
                  >
                    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      task.status === 2 ? 'bg-green-400' :
                      task.status === 1 ? 'bg-yellow-400' : 'bg-gray-300'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium truncate ${task.status === 2 ? 'line-through text-gray-400' : 'text-gray-700'}`}>
                        {task.subject}
                      </p>
                      <p className="text-xs text-gray-400 truncate">{task.taskContent}</p>
                    </div>
                    <span className="text-xs text-gray-400 flex-shrink-0">
                      {TASK_TYPE_LABELS[task.taskType]}
                    </span>
                  </div>
                ))}
              </div>
              {todayTasks.length > 4 && (
                <button
                  onClick={() => navigate('/tasks')}
                  className="w-full text-center text-sm text-blue-500 mt-3 hover:text-blue-600"
                >
                  查看全部 {todayTasks.length} 个任务 →
                </button>
              )}
            </>
          ) : (
            <p className="text-sm text-gray-400 text-center py-4">
              今天暂无学习任务，先去
              <button
                onClick={() => navigate('/plans/create')}
                className="text-blue-500 hover:text-blue-600 mx-1"
              >
                创建备考计划
              </button>
              吧~
            </p>
          )}
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-3 gap-3">
        <Link to="/plans" className="bg-white rounded-2xl p-4 shadow-sm flex flex-col items-center gap-1 hover:shadow-md transition">
          <span className="text-2xl">📋</span>
          <p className="font-medium text-gray-800 text-sm">备考计划</p>
          <p className="text-xs text-gray-400">{plans.length} 个</p>
        </Link>
        <Link to="/chat" className="bg-white rounded-2xl p-4 shadow-sm flex flex-col items-center gap-1 hover:shadow-md transition">
          <img src="/logo.png" alt="小搭" className="w-10 h-10" />
          <p className="font-medium text-gray-800 text-sm">小搭</p>
          <p className="text-xs text-gray-400">随时提问</p>
        </Link>
        <Link to="/report" className="bg-white rounded-2xl p-4 shadow-sm flex flex-col items-center gap-1 hover:shadow-md transition">
          <span className="text-2xl">📊</span>
          <p className="font-medium text-gray-800 text-sm">学习报告</p>
          <p className="text-xs text-gray-400">查看周报</p>
        </Link>
      </div>
    </div>
  )
}

function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好，夜猫子！'
  if (hour < 12) return '早上好，加油！'
  if (hour < 14) return '中午好，别忘了休息~'
  if (hour < 18) return '下午好，继续冲！'
  if (hour < 22) return '晚上好，加把劲！'
  return '深夜了，注意休息哦'
}
