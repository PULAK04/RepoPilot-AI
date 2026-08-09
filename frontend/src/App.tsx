import { Navigate, Route, Routes } from 'react-router-dom'
import { useSelector } from 'react-redux'
import type { RootState } from './store'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import RepositoryPage from './pages/RepositoryPage'
import AnalysisPage from './pages/AnalysisPage'

function Protected({ children }: { children: React.ReactNode }) {
  const token = useSelector((s: RootState) => s.auth.token)
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Protected><DashboardPage /></Protected>} />
      <Route path="/repositories/:repoId" element={<Protected><RepositoryPage /></Protected>} />
      <Route path="/analyses/:analysisId" element={<Protected><AnalysisPage /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
