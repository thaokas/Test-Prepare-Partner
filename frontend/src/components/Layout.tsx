import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { authApi } from '@/api'
import { useAuthStore } from '@/store/authStore'

const NAV_ITEMS = [
  { to: '/', label: '首页', icon: HomeIcon },
  { to: '/plans', label: '计划', icon: PlanIcon },
  { to: '/checkin', label: '打卡', icon: CheckinIcon, primary: true },
  { to: '/tasks', label: '任务', icon: TaskIcon },
  { to: '/profile', label: '我的', icon: ProfileIcon },
]

export default function Layout() {
  const { setUser, user } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (!user) {
      authApi.me()
        .then((res) => setUser(res.data.data))
        .catch(() => {
          navigate('/login', { replace: true })
        })
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col max-w-md mx-auto">
      {/* Main content */}
      <main className="flex-1 overflow-y-auto px-4 pt-4 pb-24">
        <Outlet />
      </main>

      {/* Bottom navigation */}
      <nav className="fixed bottom-0 left-0 right-0 max-w-md mx-auto bg-white border-t border-gray-100 safe-bottom">
        <div className="flex items-end h-16 px-2">
          {NAV_ITEMS.map(({ to, label, icon: Icon, primary }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex-1 flex flex-col items-center justify-center gap-0.5 py-2 transition ${
                  primary
                    ? ''
                    : isActive
                    ? 'text-blue-500'
                    : 'text-gray-400 hover:text-gray-600'
                }`
              }
            >
              {({ isActive }) =>
                primary ? (
                  <div className="w-12 h-12 bg-blue-500 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-200 -mt-4">
                    <Icon active={isActive} className="w-6 h-6 text-white" />
                  </div>
                ) : (
                  <>
                    <Icon active={isActive} className="w-6 h-6" />
                    <span className="text-xs">{label}</span>
                  </>
                )
              }
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}

// Icon components
function HomeIcon({ className, active }: { className?: string; active: boolean }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill={active ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  )
}

function PlanIcon({ className, active }: { className?: string; active: boolean }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill={active ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
    </svg>
  )
}

function CheckinIcon({ className }: { className?: string; active: boolean }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  )
}

function TaskIcon({ className, active }: { className?: string; active: boolean }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill={active ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
}

function ProfileIcon({ className, active }: { className?: string; active: boolean }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill={active ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  )
}
