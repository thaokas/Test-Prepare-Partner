import { useEffect, useState } from 'react'
import { userApi, checkinApi } from '@/api'
import { useAuthStore } from '@/store/authStore'
import { useNavigate } from 'react-router-dom'
import type { CheckinHistoryItem } from '@/types'
import Loading from '@/components/Loading'
import dayjs from 'dayjs'

export default function Profile() {
  const navigate = useNavigate()
  const { user, setUser, logout } = useAuthStore()
  const [stats, setStats] = useState({ totalCheckins: 0, currentStreak: 0, maxStreak: 0 })
  const [history, setHistory] = useState<CheckinHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [nickname, setNickname] = useState(user?.nickname ?? '')

  useEffect(() => {
    const userId = user?.userId ?? localStorage.getItem('userId')
    if (!userId) return
    Promise.all([
      userApi.getStats(userId),
      checkinApi.getHistory(
        dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
        dayjs().format('YYYY-MM-DD')
      ),
    ]).then(([statsRes, historyRes]) => {
      setStats(statsRes.data.data)
      setHistory(historyRes.data.data)
    }).finally(() => setLoading(false))
  }, [user])

  const handleSaveNickname = async () => {
    const userId = user?.userId ?? localStorage.getItem('userId')
    if (!userId || !nickname.trim()) return
    const res = await userApi.update(userId, { nickname })
    setUser(res.data.data)
    setEditing(false)
  }

  const handleLogout = () => {
    if (confirm('确定要退出登录吗？')) {
      logout()
      navigate('/login')
    }
  }

  if (loading) return <Loading />

  // Build 30-day calendar
  const last30 = Array.from({ length: 30 }, (_, i) =>
    dayjs().subtract(29 - i, 'day').format('YYYY-MM-DD')
  )
  const checkinSet = new Set(history.map((h) => h.checkinDate))

  return (
    <div className="space-y-4 pb-4">
      {/* Avatar & name */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-2xl p-5">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center text-3xl">
            {user?.avatarUrl ? (
              <img src={user.avatarUrl} alt="avatar" className="w-16 h-16 rounded-full object-cover" />
            ) : (
              '👤'
            )}
          </div>
          <div className="flex-1">
            {editing ? (
              <div className="flex items-center gap-2">
                <input
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  className="bg-white/20 text-white placeholder-white/60 px-3 py-1.5 rounded-lg text-sm w-32 focus:outline-none"
                  maxLength={20}
                />
                <button onClick={handleSaveNickname} className="text-sm bg-white text-blue-500 px-2 py-1 rounded-lg">
                  保存
                </button>
                <button onClick={() => setEditing(false)} className="text-sm text-white/70">
                  取消
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <p className="text-lg font-bold">{user?.nickname}</p>
                <button onClick={() => setEditing(true)} className="text-white/60 text-sm">✏️</button>
              </div>
            )}
            <p className="text-blue-100 text-sm">{user?.email}</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: '累计打卡', value: stats.totalCheckins, color: 'text-blue-500' },
          { label: '当前连续', value: stats.currentStreak, color: 'text-green-500' },
          { label: '最长连续', value: stats.maxStreak, color: 'text-orange-500' },
        ].map((item) => (
          <div key={item.label} className="bg-white rounded-2xl p-4 shadow-sm text-center">
            <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
            <p className="text-xs text-gray-400 mt-1">{item.label}</p>
          </div>
        ))}
      </div>

      {/* 30-day calendar */}
      <div className="bg-white rounded-2xl p-4 shadow-sm">
        <p className="font-medium text-gray-700 mb-3">最近30天打卡记录</p>
        <div className="grid grid-cols-10 gap-1.5">
          {last30.map((date) => (
            <div
              key={date}
              title={date}
              className={`w-full aspect-square rounded-md ${
                checkinSet.has(date) ? 'bg-green-400' : 'bg-gray-100'
              }`}
            />
          ))}
        </div>
        <div className="flex items-center gap-2 mt-2 text-xs text-gray-400">
          <div className="w-3 h-3 rounded-sm bg-gray-100" />
          <span>未打卡</span>
          <div className="w-3 h-3 rounded-sm bg-green-400 ml-2" />
          <span>已打卡</span>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <button
          onClick={() => navigate('/reminders')}
          className="w-full px-4 py-4 text-left text-gray-700 text-sm font-medium hover:bg-gray-50 transition flex items-center gap-3 border-b border-gray-100"
        >
          <span>⏰</span>
          提醒设置
        </button>
        <button
          onClick={() => navigate('/report')}
          className="w-full px-4 py-4 text-left text-gray-700 text-sm font-medium hover:bg-gray-50 transition flex items-center gap-3 border-b border-gray-100"
        >
          <span>📊</span>
          学习周报
        </button>
        <button
          onClick={handleLogout}
          className="w-full px-4 py-4 text-left text-red-500 text-sm font-medium hover:bg-red-50 transition flex items-center gap-3"
        >
          <span>🚪</span>
          退出登录
        </button>
      </div>

      <p className="text-center text-xs text-gray-300">备考搭子 · PrepKeeper</p>
    </div>
  )
}
