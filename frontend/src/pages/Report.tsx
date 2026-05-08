import { useState } from 'react'
import { agentApi } from '@/api'
import type { WeeklyReportResponse } from '@/types'
import ProgressBar from '@/components/ProgressBar'
import dayjs from 'dayjs'

export default function Report() {
  const [weekStart, setWeekStart] = useState(
    dayjs().startOf('week').add(1, 'day').format('YYYY-MM-DD')
  )
  const [weekEnd, setWeekEnd] = useState(
    dayjs().endOf('week').format('YYYY-MM-DD')
  )
  const [report, setReport] = useState<WeeklyReportResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (dayjs(weekStart).isAfter(weekEnd)) {
      setError('开始日期不能晚于结束日期')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await agentApi.getWeeklyReport({ weekStart, weekEnd })
      setReport(res.data.data)
    } catch {
      setError('生成报告失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const completionRate = report?.completionRate ?? 0
  const subjectBreakdown = report?.subjectBreakdown ?? {}
  const suggestions = report?.suggestions ?? []

  // Colors for subject bars
  const subjectColors = ['bg-blue-400', 'bg-green-400', 'bg-orange-400', 'bg-purple-400', 'bg-pink-400', 'bg-teal-400']
  const entries = Object.entries(subjectBreakdown)
  const totalForBar = entries.reduce((sum, [, v]) => sum + v, 0)

  return (
    <div className="space-y-4 pb-4">
      <h2 className="text-lg font-bold text-gray-800">学习周报</h2>

      {/* Date pickers */}
      <div className="bg-white rounded-2xl p-4 shadow-sm space-y-3">
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <label className="block text-xs text-gray-500 mb-1">开始日期</label>
            <input
              type="date"
              value={weekStart}
              onChange={(e) => setWeekStart(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <span className="text-gray-400 pt-5">至</span>
          <div className="flex-1">
            <label className="block text-xs text-gray-500 mb-1">结束日期</label>
            <input
              type="date"
              value={weekEnd}
              onChange={(e) => setWeekEnd(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-blue-500 disabled:bg-blue-300 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-blue-600 transition"
        >
          {loading ? 'AI 正在生成报告...' : '📊 生成周报'}
        </button>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-3 rounded-xl">
            {error}
          </div>
        )}
      </div>

      {/* Report result */}
      {loading && (
        <div className="bg-white rounded-2xl p-8 shadow-sm text-center">
          <div className="text-4xl mb-3">🤖</div>
          <p className="text-gray-500 text-sm">AI 正在分析你的学习数据，生成专属周报...</p>
          <div className="mt-4 w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
            <div className="bg-blue-500 h-full rounded-full animate-pulse w-3/4" />
          </div>
        </div>
      )}

      {report && !loading && (
        <div className="space-y-4">
          {/* Overview stats */}
          <div className="bg-white rounded-2xl p-5 shadow-sm">
            <h3 className="font-semibold text-gray-800 mb-4">
              {report.weekStart ?? weekStart} ~ {report.weekEnd ?? weekEnd} 学习概览
            </h3>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div>
                <p className="text-2xl font-bold text-blue-500">{report.completedTasks ?? 0}</p>
                <p className="text-xs text-gray-400">完成任务</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-500">
                  {Math.round(completionRate * 100)}%
                </p>
                <p className="text-xs text-gray-400">完成率</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-orange-500">{report.totalHours ?? 0}h</p>
                <p className="text-xs text-gray-400">学习时长</p>
              </div>
            </div>
            <div className="mt-3">
              <ProgressBar value={report.completedTasks ?? 0} max={report.totalTasks ?? 1} showLabel />
            </div>
          </div>

          {/* Subject breakdown */}
          {entries.length > 0 && (
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-800 mb-3">科目分布</h3>
              <div className="space-y-3">
                {entries.map(([subject, hours], idx) => (
                  <div key={subject}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-700">{subject}</span>
                      <span className="text-xs text-gray-400">{hours}h</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div
                        className={`${subjectColors[idx % subjectColors.length]} h-2 rounded-full transition-all`}
                        style={{ width: `${totalForBar > 0 ? (hours / totalForBar) * 100 : 0}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI suggestions */}
          {suggestions.length > 0 && (
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-800 mb-3">AI 学习建议</h3>
              <ul className="space-y-2">
                {suggestions.map((s, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                    <span className="text-blue-400 mt-0.5">💡</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* No data fallback */}
          {entries.length === 0 && suggestions.length === 0 && (
            <div className="bg-white rounded-2xl p-8 shadow-sm text-center">
              <p className="text-gray-400 text-sm">本周暂无详细数据</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
