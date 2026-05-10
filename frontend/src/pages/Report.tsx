import { useState } from 'react'
import { agentApi } from '@/api'
import type { WeeklyReportResponse, SubjectStat, DailyBreakdown } from '@/types'
import ProgressBar from '@/components/ProgressBar'
import dayjs from 'dayjs'

// ── 等级配置 ──────────────────────────────────────────────────────────────────
const GRADE_CONFIG: Record<string, { label: string; color: string; bg: string; text: string }> = {
  S: { label: 'S', color: 'bg-yellow-400', bg: 'bg-yellow-50', text: 'text-yellow-600' },
  A: { label: 'A', color: 'bg-green-400', bg: 'bg-green-50', text: 'text-green-600' },
  B: { label: 'B', color: 'bg-blue-400', bg: 'bg-blue-50', text: 'text-blue-600' },
  C: { label: 'C', color: 'bg-orange-400', bg: 'bg-orange-50', text: 'text-orange-600' },
  D: { label: 'D', color: 'bg-red-400', bg: 'bg-red-50', text: 'text-red-600' },
}

function getGradeInfo(rate: number) {
  if (rate >= 95) return GRADE_CONFIG.S
  if (rate >= 80) return GRADE_CONFIG.A
  if (rate >= 60) return GRADE_CONFIG.B
  if (rate >= 30) return GRADE_CONFIG.C
  return GRADE_CONFIG.D
}

// ── 日期快捷选项 ──────────────────────────────────────────────────────────────
const DATE_PRESETS = [
  { label: '本周', get: () => [dayjs().startOf('week').add(1, 'day'), dayjs().endOf('week')] },
  { label: '上周', get: () => [dayjs().subtract(1, 'week').startOf('week').add(1, 'day'), dayjs().subtract(1, 'week').endOf('week')] },
  { label: '近3天', get: () => [dayjs().subtract(2, 'day'), dayjs()] },
  { label: '近7天', get: () => [dayjs().subtract(6, 'day'), dayjs()] },
  { label: '本月', get: () => [dayjs().startOf('month'), dayjs()] },
]

// ── 科目颜色 ──────────────────────────────────────────────────────────────────
const SUBJECT_COLORS = ['bg-blue-400', 'bg-green-400', 'bg-orange-400', 'bg-purple-400', 'bg-pink-400', 'bg-teal-400']

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

  const handlePreset = (preset: (typeof DATE_PRESETS)[number]) => {
    const [s, e] = preset.get()
    setWeekStart(s.format('YYYY-MM-DD'))
    setWeekEnd(e.format('YYYY-MM-DD'))
    setReport(null)
    setError('')
  }

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

  // ── 从响应中提取数据 ────────────────────────────────────────────────────────
  const completionRate = report?.completionRate ?? 0
  const totalTasks = report?.totalTasks ?? 0
  const completedTasks = report?.completedTasks ?? 0
  const totalHours = report?.totalHours ?? 0
  const streakDays = report?.streakDays ?? 0
  const grade = report?.grade ?? getGradeInfo(completionRate).label
  const suggestions = report?.suggestions ?? []
  const subjectBreakdown = report?.subjectBreakdown ?? {}
  const subjectStats = report?.subjectStats ?? []
  const dailyBreakdown = report?.dailyBreakdown ?? []
  const gradeInfo = getGradeInfo(completionRate)
  const reportTitle = report?.reportTitle ?? '学习报告'
  const dateLabel = `${weekStart} ~ ${weekEnd}`

  const entries = Object.entries(subjectBreakdown)
  const totalForBar = entries.reduce((sum, [, v]) => sum + v, 0)

  return (
    <div className="space-y-4 pb-6">
      <h2 className="text-lg font-bold text-gray-800">学习报告</h2>

      {/* ── 日期选择区 ──────────────────────────────────────────────────── */}
      <div className="bg-white rounded-2xl p-4 shadow-sm space-y-3">
        {/* 快捷选项 */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          {DATE_PRESETS.map((p) => (
            <button
              key={p.label}
              onClick={() => handlePreset(p)}
              className="flex-shrink-0 px-3 py-1.5 text-xs rounded-xl border border-gray-200 text-gray-600 hover:bg-blue-50 hover:border-blue-300 transition"
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* 自定义日期 */}
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <label className="block text-xs text-gray-500 mb-1">开始日期</label>
            <input
              type="date"
              value={weekStart}
              onChange={(e) => { setWeekStart(e.target.value); setReport(null) }}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <span className="text-gray-400 pt-5">至</span>
          <div className="flex-1">
            <label className="block text-xs text-gray-500 mb-1">结束日期</label>
            <input
              type="date"
              value={weekEnd}
              onChange={(e) => { setWeekEnd(e.target.value); setReport(null) }}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-blue-500 disabled:bg-blue-300 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-blue-600 transition"
        >
          {loading ? 'AI 正在分析数据...' : '📊 生成报告'}
        </button>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-3 rounded-xl">
            {error}
          </div>
        )}
      </div>

      {/* ── 加载状态 ────────────────────────────────────────────────────── */}
      {loading && (
        <div className="bg-white rounded-2xl p-8 shadow-sm text-center">
          <img src="/logo.png" alt="小搭" className="w-10 h-10 mb-3 mx-auto" />
          <p className="text-gray-500 text-sm">AI 正在分析你的学习数据，生成专属报告...</p>
          <div className="mt-4 w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
            <div className="bg-blue-500 h-full rounded-full animate-pulse w-3/4" />
          </div>
        </div>
      )}

      {/* ── 报告结果 ────────────────────────────────────────────────────── */}
      {report && !loading && (
        <div className="space-y-4">
          {/* 等级 + 标题 */}
          <div className="bg-white rounded-2xl p-5 shadow-sm">
            <div className="flex items-center gap-4">
              <div className={`w-16 h-16 rounded-full ${gradeInfo.bg} flex items-center justify-center`}>
                <span className={`text-3xl font-extrabold ${gradeInfo.text}`}>{grade}</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 text-base">{reportTitle}</h3>
                <p className="text-xs text-gray-400 mt-0.5">{dateLabel}</p>
              </div>
            </div>
          </div>

          {/* 总览统计 */}
          <div className="bg-white rounded-2xl p-5 shadow-sm">
            <h3 className="font-semibold text-gray-800 mb-4">学习概览</h3>
            <div className="grid grid-cols-4 gap-3 text-center">
              <div>
                <p className="text-2xl font-bold text-blue-500">{completedTasks}</p>
                <p className="text-xs text-gray-400">完成任务</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-500">
                  {Math.round(completionRate)}%
                </p>
                <p className="text-xs text-gray-400">完成率</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-orange-500">{totalHours}h</p>
                <p className="text-xs text-gray-400">学习时长</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-500">{streakDays}</p>
                <p className="text-xs text-gray-400">打卡天数</p>
              </div>
            </div>
            <div className="mt-4">
              <ProgressBar value={completedTasks} max={totalTasks || 1} showLabel />
            </div>
          </div>

          {/* 每日进度 */}
          {dailyBreakdown.length > 0 && (
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-800 mb-3">每日进度</h3>
              <div className="space-y-3">
                {dailyBreakdown.map((day: DailyBreakdown) => {
                  const d = dayjs(day.date)
                  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
                  const dayLabel = `${d.month() + 1}月${d.date()}日 周${weekdays[d.day()]}`
                  const barColor =
                    day.rate >= 80 ? 'bg-green-400' :
                    day.rate >= 50 ? 'bg-orange-400' :
                    day.planned_count > 0 ? 'bg-red-400' : 'bg-gray-300'
                  return (
                    <div key={day.date}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-700">{dayLabel}</span>
                        <span className="text-xs text-gray-400">
                          完成 {day.completed_count}/{day.planned_count} · {day.rate}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2">
                        <div
                          className={`${barColor} h-2 rounded-full transition-all`}
                          style={{ width: `${Math.min(day.rate, 100)}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* 科目分布 */}
          {subjectStats.length > 0 && (
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-800 mb-3">科目明细</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-400 text-xs">
                      <th className="pb-2 font-normal">科目</th>
                      <th className="pb-2 font-normal text-center">计划</th>
                      <th className="pb-2 font-normal text-center">完成</th>
                      <th className="pb-2 font-normal text-right">完成率</th>
                    </tr>
                  </thead>
                  <tbody>
                    {subjectStats.map((s: SubjectStat) => (
                      <tr key={s.subject} className="border-b border-gray-50">
                        <td className="py-2.5 text-gray-700">{s.subject}</td>
                        <td className="py-2.5 text-center text-gray-500">{s.planned}</td>
                        <td className="py-2.5 text-center text-gray-500">{s.completed}</td>
                        <td className="py-2.5 text-right">
                          <span className={
                            s.rate >= 80 ? 'text-green-500 font-medium' :
                            s.rate >= 50 ? 'text-orange-500 font-medium' :
                            'text-red-500 font-medium'
                          }>
                            {s.rate}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 科目分布柱状图 (备用展示) */}
          {entries.length > 0 && subjectStats.length === 0 && (
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
                        className={`${SUBJECT_COLORS[idx % SUBJECT_COLORS.length]} h-2 rounded-full transition-all`}
                        style={{ width: `${totalForBar > 0 ? (hours / totalForBar) * 100 : 0}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI 点评摘要 */}
          {report.summary && (
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-800 mb-2">AI 点评</h3>
              <p className="text-sm text-gray-600 leading-relaxed">{report.summary}</p>
            </div>
          )}

          {/* AI 学习建议 */}
          {suggestions.length > 0 && (
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-800 mb-3">学习建议</h3>
              <ul className="space-y-2">
                {suggestions.map((s, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                    <span className="text-blue-400 mt-0.5 flex-shrink-0">💡</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* HTML 报告渲染（如有） */}
          {report.htmlContent && (
            <div className="bg-white rounded-2xl p-4 shadow-sm overflow-hidden">
              <div
                dangerouslySetInnerHTML={{ __html: report.htmlContent }}
                className="report-html-content"
              />
            </div>
          )}

          {/* 无数据提示 */}
          {totalTasks === 0 && (
            <div className="bg-white rounded-2xl p-8 shadow-sm text-center">
              <p className="text-gray-400 text-sm">该时间段暂无学习数据</p>
              <p className="text-gray-300 text-xs mt-1">请选择有打卡记录的日期范围</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
