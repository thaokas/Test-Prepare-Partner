export default function Empty({ text = '暂无数据' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-gray-400">
      <svg className="w-16 h-16 mb-3 text-gray-200" fill="none" viewBox="0 0 64 64" stroke="currentColor">
        <circle cx="32" cy="32" r="28" strokeWidth="2" />
        <path d="M22 32h20M32 22v20" strokeWidth="2" strokeLinecap="round" />
      </svg>
      <span className="text-sm">{text}</span>
    </div>
  )
}
