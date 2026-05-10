import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import SplashScreen from '@/components/SplashScreen'
import Layout from '@/components/Layout'
import ProtectedRoute from '@/components/ProtectedRoute'
import Login from '@/pages/Login'
import Register from '@/pages/Register'
import Home from '@/pages/Home'
import Plans from '@/pages/Plans'
import PlanCreate from '@/pages/PlanCreate'
import PlanDetail from '@/pages/PlanDetail'
import Tasks from '@/pages/Tasks'
import Checkin from '@/pages/Checkin'
import Profile from '@/pages/Profile'
import Chat from '@/pages/Chat'
import Reminders from '@/pages/Reminders'
import Report from '@/pages/Report'

export default function App() {
  return (
    <BrowserRouter>
      <SplashScreen />
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes with shared layout */}
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<Home />} />
          <Route path="/plans" element={<Plans />} />
          <Route path="/plans/create" element={<PlanCreate />} />
          <Route path="/plans/:planId" element={<PlanDetail />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/checkin" element={<Checkin />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/reminders" element={<Reminders />} />
          <Route path="/report" element={<Report />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
