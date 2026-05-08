interface Props {
  value: number
  max?: number
  className?: string
  showLabel?: boolean
  color?: string
}

export default function ProgressBar({ value, max = 100, className = '', showLabel = false, color = 'bg-blue-500' }: Props) {
  const percent = Math.min(Math.round((value / max) * 100), 100)
  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>进度</span>
          <span>{percent}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div
          className={`h-2.5 rounded-full transition-all duration-300 ${color}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}
