import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { planApi } from '@/api'
import type { PlanCreateRequest, SupervisionMode, FoundationLevel } from '@/types'
import { SUPERVISION_MODE_LABELS, SUPERVISION_MODE_DESC, FOUNDATION_LABELS } from '@/types'
import dayjs from 'dayjs'

const EXAM_TYPES = ['考研', '四六级', '考公', '注会', '司法', '雅思', '托福', '其他']
const COMMON_SUBJECTS = ['数学', '英语', '政治', '专业课', '语文', '物理', '化学', '生物', '历史', '地理']

export default function PlanCreate() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState<PlanCreateRequest>({
    examName: '',
    examType: '',
    examDate: '',
    dailyHours: 4,
    foundationLevel: 1,
    weakSubjects: [],
    currentMode: 1,
  })

  const handleSubjectToggle = (subject: string) => {
    setForm((prev) => ({
      ...prev,
      weakSubjects: prev.weakSubjects.includes(subject)
        ? prev.weakSubjects.filter((s) => s !== subject)
        : [...prev.weakSubjects, subject],
    }))
  }

  const handleSubmit = async () => {
    setError('')
    if (!form.examName.trim()) { setError('请填写考试名称'); return }
    if (!form.examType) { setError('请选择考试类型'); return }
    if (!form.examDate) { setError('请选择考试日期'); return }
    if (dayjs(form.examDate).isBefore(dayjs())) { setError('考试日期必须在今天之后'); return }

    setLoading(true)
    try {
      const res = await planApi.create(form)
      navigate(`/plans/${res.data.data.planId}`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      setError(msg || '创建失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="pb-4">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex gap-1.5">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`h-1.5 rounded-full transition-all ${
                s <= step ? 'w-8 bg-blue-500' : 'w-4 bg-gray-200'
              }`}
            />
          ))}
        </div>
        <span className="text-xs text-gray-400">步骤 {step}/3</span>
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-800">基本信息</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">考试名称</label>
            <input
              type="text"
              value={form.examName}
              onChange={(e) => setForm({ ...form, examName: e.target.value })}
              placeholder="例如：2025年考研数学"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">考试类型</label>
            <div className="flex flex-wrap gap-2">
              {EXAM_TYPES.map((type) => (
                <button
                  key={type}
                  onClick={() => setForm({ ...form, examType: type })}
                  className={`px-3 py-1.5 rounded-xl text-sm border transition ${
                    form.examType === type
                      ? 'bg-blue-500 text-white border-blue-500'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">考试日期</label>
            <input
              type="date"
              value={form.examDate}
              min={dayjs().add(1, 'day').format('YYYY-MM-DD')}
              onChange={(e) => setForm({ ...form, examDate: e.target.value })}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          </div>

          <button
            onClick={() => {
              if (!form.examName.trim() || !form.examType || !form.examDate) {
                setError('请填写所有必填项')
                return
              }
              setError('')
              setStep(2)
            }}
            className="w-full bg-blue-500 text-white py-3 rounded-xl font-medium hover:bg-blue-600 transition"
          >
            下一步
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-800">学习规划</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              每日学习时长：<span className="text-blue-500">{form.dailyHours}小时</span>
            </label>
            <input
              type="range"
              min={0.5}
              max={12}
              step={0.5}
              value={form.dailyHours}
              onChange={(e) => setForm({ ...form, dailyHours: Number(e.target.value) })}
              className="w-full accent-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>0.5h</span><span>12h</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">基础水平</label>
            <div className="grid grid-cols-3 gap-2">
              {([0, 1, 2] as FoundationLevel[]).map((level) => (
                <button
                  key={level}
                  onClick={() => setForm({ ...form, foundationLevel: level })}
                  className={`py-3 rounded-xl text-sm border transition ${
                    form.foundationLevel === level
                      ? 'bg-blue-500 text-white border-blue-500'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'
                  }`}
                >
                  {FOUNDATION_LABELS[level]}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              薄弱科目（可多选）
            </label>
            <div className="flex flex-wrap gap-2">
              {COMMON_SUBJECTS.map((subject) => (
                <button
                  key={subject}
                  onClick={() => handleSubjectToggle(subject)}
                  className={`px-3 py-1.5 rounded-xl text-sm border transition ${
                    form.weakSubjects.includes(subject)
                      ? 'bg-orange-400 text-white border-orange-400'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-orange-300'
                  }`}
                >
                  {subject}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(1)}
              className="flex-1 border border-gray-200 text-gray-600 py-3 rounded-xl font-medium hover:bg-gray-50 transition"
            >
              上一步
            </button>
            <button
              onClick={() => setStep(3)}
              className="flex-1 bg-blue-500 text-white py-3 rounded-xl font-medium hover:bg-blue-600 transition"
            >
              下一步
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-800">督促模式</h2>
          <p className="text-sm text-gray-500">选择你想要的督促方式，之后可以随时修改</p>

          <div className="space-y-3">
            {([0, 1, 2, 3] as SupervisionMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setForm({ ...form, currentMode: mode })}
                className={`w-full text-left px-4 py-4 rounded-xl border transition ${
                  form.currentMode === mode
                    ? 'bg-blue-50 border-blue-400'
                    : 'bg-white border-gray-200 hover:border-blue-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-800">{SUPERVISION_MODE_LABELS[mode]}</span>
                  {form.currentMode === mode && (
                    <span className="text-blue-500 text-lg">✓</span>
                  )}
                </div>
                <p className="text-xs text-gray-400 mt-1">{SUPERVISION_MODE_DESC[mode]}</p>
              </button>
            ))}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-3 rounded-xl">
              {error}
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={() => setStep(2)}
              className="flex-1 border border-gray-200 text-gray-600 py-3 rounded-xl font-medium hover:bg-gray-50 transition"
            >
              上一步
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex-1 bg-blue-500 disabled:bg-blue-300 text-white py-3 rounded-xl font-medium hover:bg-blue-600 transition"
            >
              {loading ? '生成计划中...' : '🚀 生成计划'}
            </button>
          </div>
          {loading && (
            <p className="text-center text-sm text-gray-400">AI 正在为你定制学习计划，请稍等...</p>
          )}
        </div>
      )}

      {step < 3 && error && (
        <div className="mt-3 bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-3 rounded-xl">
          {error}
        </div>
      )}
    </div>
  )
}
