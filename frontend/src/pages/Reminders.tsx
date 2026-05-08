import { useEffect, useState } from 'react'
import { reminderApi, planApi } from '@/api'
import { useAuthStore } from '@/store/authStore'
import type { Reminder, ReminderSettingsResponse, PlanResponse } from '@/types'
import { REMINDER_TYPE_LABELS, SUPERVISION_MODE_LABELS, SUPERVISION_MODE_DESC } from '@/types'
import Loading from '@/components/Loading'
import Empty from '@/components/Empty'
import dayjs from 'dayjs'

export default function Reminders() {
  const user = useAuthStore((s) => s.user)
  const [activeTab, setActiveTab] = useState<'settings' | 'history'>('settings')
  const [loading, setLoading] = useState(true)

  return (
    <div className="space-y-4 pb-4">
      <h2 className="text-lg font-bold text-gray-800">提醒管理</h2>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1">
        <button
          onClick={() => setActiveTab('settings')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === 'settings' ? 'bg-white text-blue-500 shadow-sm' : 'text-gray-500'
          }`}
        >
          提醒设置
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === 'history' ? 'bg-white text-blue-500 shadow-sm' : 'text-gray-500'
          }`}
        >
          提醒历史
        </button>
      </div>

      {activeTab === 'settings' ? (
        <ReminderSettings onLoaded={() => setLoading(false)} />
      ) : (
        <ReminderHistory onLoaded={() => setLoading(false)} />
      )}

      {loading && <Loading />}
    </div>
  )
}

function ReminderSettings({ onLoaded }: { onLoaded: () => void }) {
  const user = useAuthStore((s) => s.user)

  const [plans, setPlans] = useState<PlanResponse[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState('')
  const [settings, setSettings] = useState<ReminderSettingsResponse | null>(null)
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  // Local form state
  const [mode, setMode] = useState(1)
  const [customTimes, setCustomTimes] = useState<string[]>(['21:00'])
  const [monkingInterval, setMonkingInterval] = useState(30)
  const [isActive, setIsActive] = useState(true)

  useEffect(() => {
    const userId = user?.userId ?? localStorage.getItem('userId')
    if (!userId) return

    planApi.getByUser(userId).then((planRes) => {
      const active = planRes.data.data.filter((p) => p.planStatus === 0)
      setPlans(active)
      if (active.length > 0) {
        setSelectedPlanId(active[0].planId)
      }
    })

    reminderApi.getSettings().then((res) => {
      const s = res.data.data
      setSettings(s)
      setMode(s.mode)
      setCustomTimes(s.customTimes ?? ['21:00'])
      setMonkingInterval(s.monkingInterval ?? 30)
      setIsActive(s.isActive)
    }).finally(() => onLoaded())
  }, [user])

  const handleAddTime = () => {
    if (customTimes.length >= 5) return
    setCustomTimes([...customTimes, ''])
  }

  const handleRemoveTime = (idx: number) => {
    setCustomTimes(customTimes.filter((_, i) => i !== idx))
  }

  const handleTimeChange = (idx: number, val: string) => {
    setCustomTimes(customTimes.map((t, i) => (i === idx ? val : t)))
  }

  const handleSave = async () => {
    if (!selectedPlanId) {
      setMsg('请先选择一个备考计划')
      return
    }
    const validTimes = customTimes.filter((t) => t.trim())
    if (validTimes.length === 0) {
      setMsg('请至少设置一个提醒时间')
      return
    }
    setSaving(true)
    setMsg('')
    try {
      await reminderApi.updateConfig({
        planId: selectedPlanId,
        mode,
        customTimes: validTimes,
        monkingInterval,
      })
      setMsg('设置已保存')
    } catch {
      setMsg('保存失败，请稍后重试')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Plan selector */}
      {plans.length > 1 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">关联计划</label>
          <div className="flex gap-2 flex-wrap">
            {plans.map((plan) => (
              <button
                key={plan.planId}
                onClick={() => setSelectedPlanId(plan.planId)}
                className={`px-3 py-1.5 rounded-xl text-sm border transition ${
                  selectedPlanId === plan.planId
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white text-gray-600 border-gray-200'
                }`}
              >
                {plan.examName}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Mode selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">督促模式</label>
        <div className="space-y-2">
          {([0, 1, 2, 3] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`w-full text-left px-4 py-3 rounded-xl border transition ${
                mode === m ? 'bg-blue-50 border-blue-400' : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium text-sm">{SUPERVISION_MODE_LABELS[m]}</span>
                {mode === m && <span className="text-blue-500">✓</span>}
              </div>
              <p className="text-xs text-gray-400 mt-0.5">{SUPERVISION_MODE_DESC[m]}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Custom times */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-gray-700">自定义提醒时间</label>
          <button
            onClick={handleAddTime}
            disabled={customTimes.length >= 5}
            className="text-xs text-blue-500 disabled:text-gray-300"
          >
            + 添加时间
          </button>
        </div>
        <div className="space-y-2">
          {customTimes.map((time, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <input
                type="time"
                value={time}
                onChange={(e) => handleTimeChange(idx, e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {customTimes.length > 1 && (
                <button
                  onClick={() => handleRemoveTime(idx)}
                  className="text-red-400 text-sm px-2"
                >
                  删除
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Monking interval (only shown for Tangseng mode) */}
      {mode === 3 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            唐僧模式间隔：{monkingInterval} 分钟
          </label>
          <input
            type="range"
            min={10}
            max={120}
            step={5}
            value={monkingInterval}
            onChange={(e) => setMonkingInterval(Number(e.target.value))}
            className="w-full accent-blue-500"
          />
          <div className="flex justify-between text-xs text-gray-400">
            <span>10分钟</span>
            <span>120分钟</span>
          </div>
        </div>
      )}

      {/* Active toggle */}
      <div className="flex items-center justify-between bg-white rounded-xl p-3 shadow-sm">
        <span className="text-sm font-medium text-gray-700">启用提醒</span>
        <button
          onClick={() => setIsActive(!isActive)}
          className={`w-12 h-7 rounded-full transition relative ${
            isActive ? 'bg-blue-500' : 'bg-gray-300'
          }`}
        >
          <div className={`w-5 h-5 bg-white rounded-full absolute top-1 transition ${
            isActive ? 'left-6' : 'left-1'
          }`} />
        </button>
      </div>

      {/* Message */}
      {msg && (
        <div className={`text-sm px-4 py-3 rounded-xl ${
          msg.includes('失败') ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'
        }`}>
          {msg}
        </div>
      )}

      {/* Save button */}
      <button
        onClick={handleSave}
        disabled={saving}
        className="w-full bg-blue-500 disabled:bg-blue-300 text-white py-3 rounded-xl font-medium hover:bg-blue-600 transition"
      >
        {saving ? '保存中...' : '保存设置'}
      </button>
    </div>
  )
}

function ReminderHistory({ onLoaded }: { onLoaded: () => void }) {
  const [history, setHistory] = useState<Reminder[]>([])

  useEffect(() => {
    reminderApi.getHistory()
      .then((res) => setHistory(res.data.data))
      .finally(() => onLoaded())
  }, [])

  if (history.length === 0) return <Empty text="暂无提醒记录" />

  return (
    <div className="space-y-2">
      {history.map((r) => (
        <div key={r.reminderId} className="bg-white rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs bg-blue-50 text-blue-500 px-2 py-0.5 rounded-full">
              {REMINDER_TYPE_LABELS[r.reminderType]}
            </span>
            <span className={`text-xs ${r.isSent ? 'text-green-500' : 'text-gray-400'}`}>
              {r.isSent ? '已发送' : '未发送'}
            </span>
          </div>
          <p className="text-sm text-gray-700 mt-2">{r.content || '（无内容）'}</p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-400">
              {dayjs(r.triggerTime).format('M月D日 HH:mm')}
            </span>
            {r.sentAt && (
              <span className="text-xs text-gray-400">
                发送于 {dayjs(r.sentAt).format('HH:mm')}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
