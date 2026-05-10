import { useState, useEffect } from 'react'

export default function SplashScreen() {
  const [visible, setVisible] = useState(true)
  const [fadeOut, setFadeOut] = useState(false)

  useEffect(() => {
    const shown = sessionStorage.getItem('splash_shown')
    if (shown) {
      setVisible(false)
      return
    }

    const timer = setTimeout(() => {
      setFadeOut(true)
      setTimeout(() => {
        setVisible(false)
        sessionStorage.setItem('splash_shown', '1')
      }, 600)
    }, 1800)

    return () => clearTimeout(timer)
  }, [])

  if (!visible) return null

  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-white transition-opacity duration-500 ${
        fadeOut ? 'opacity-0' : 'opacity-100'
      }`}
    >
      <div className="animate-[fadeIn_0.6s_ease-out]">
        <img
          src="/logo.png"
          alt="prepKeeper"
          className="w-48 h-48 object-contain rounded-2xl shadow-lg"
        />
      </div>
      <p className="mt-6 text-gray-400 text-sm tracking-wider animate-[fadeIn_0.8s_ease-out]">
        prepKeeper
      </p>
    </div>
  )
}
