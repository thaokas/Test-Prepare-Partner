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
      className={`fixed inset-0 z-50 transition-opacity duration-500 ${
        fadeOut ? 'opacity-0' : 'opacity-100'
      }`}
    >
      <img
        src="/background.jpg"
        alt="prepKeeper"
        className="absolute inset-0 w-full h-full object-cover"
      />
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="animate-[fadeIn_0.6s_ease-out]">
          <img
            src="/logo-start.png"
            alt="prepKeeper"
            className="w-48 h-48 object-contain rounded-2xl shadow-lg"
          />
        </div>
        <p className="mt-6 text-gray-400 text-sm tracking-wider text-center animate-[fadeIn_0.8s_ease-out]">
          备考搭子
          <br />
          Study Buddy
        </p>
      </div>
    </div>
  )
}
