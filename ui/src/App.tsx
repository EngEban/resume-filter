import { Route, Routes } from 'react-router-dom';
import { AppLayout } from './components/AppLayout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { PublicLayout } from './components/PublicLayout';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import NotFoundPage from './pages/NotFoundPage';
import RegisterPage from './pages/RegisterPage';

import AnalyzeResumePage from './pages/AnalyzeResumePage';
import B2CDashboardPage from './pages/B2CDashboardPage';
import HistoryPage from './pages/HistoryPage';
import SettingsPage from './pages/SettingsPage';

import B2BAnalyticsOverviewPage from './pages/B2BAnalyticsOverviewPage';
import B2BAnalyticsPage from './pages/B2BAnalyticsPage';
import B2BBatchDetailsPage from './pages/B2BBatchDetailsPage';
import B2BBatchesPage from './pages/B2BBatchesPage';
import B2BNewBatchPage from './pages/B2BNewBatchPage';
import B2BCandidatesPage from './pages/B2BCandidatesPage';
import B2BComparePage from './pages/B2BComparePage';
import B2BDashboardPage from './pages/B2BDashboardPage';
import B2BExportsPage from './pages/B2BExportsPage';
import B2BResumeDetailsPage from './pages/B2BResumeDetailsPage';
import B2BSettingsPage from './pages/B2BSettingsPage';

function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<PublicLayout><LandingPage /></PublicLayout>} />
      <Route path="/login" element={<PublicLayout showHeader={false} showFooter={false}><LoginPage /></PublicLayout>} />
      <Route path="/register" element={<PublicLayout showHeader={false} showFooter={false}><RegisterPage /></PublicLayout>} />

      {/* B2C */}
      <Route path="/dashboard" element={<ProtectedRoute requiredAccountType="b2c"><AppLayout><B2CDashboardPage /></AppLayout></ProtectedRoute>} />
      <Route path="/analyze" element={<ProtectedRoute requiredAccountType="b2c"><AppLayout><AnalyzeResumePage /></AppLayout></ProtectedRoute>} />
      <Route path="/history" element={<ProtectedRoute requiredAccountType="b2c"><AppLayout><HistoryPage /></AppLayout></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute requiredAccountType="b2c"><AppLayout><SettingsPage /></AppLayout></ProtectedRoute>} />

      {/* B2B */}
      <Route path="/b2b/dashboard" element={<ProtectedRoute requiredAccountType="b2b"><B2BDashboardPage /></ProtectedRoute>} />
      <Route path="/b2b/batches" element={<ProtectedRoute requiredAccountType="b2b"><B2BBatchesPage /></ProtectedRoute>} />
      <Route path="/b2b/batches/new" element={<ProtectedRoute requiredAccountType="b2b"><B2BNewBatchPage /></ProtectedRoute>} />
      <Route path="/b2b/batches/:batchId" element={<ProtectedRoute requiredAccountType="b2b"><B2BBatchDetailsPage /></ProtectedRoute>} />
      <Route path="/b2b/batches/:batchId/analytics" element={<ProtectedRoute requiredAccountType="b2b"><B2BAnalyticsPage /></ProtectedRoute>} />
      <Route path="/b2b/batches/:batchId/compare" element={<ProtectedRoute requiredAccountType="b2b"><B2BComparePage /></ProtectedRoute>} />
      <Route path="/b2b/candidates" element={<ProtectedRoute requiredAccountType="b2b"><B2BCandidatesPage /></ProtectedRoute>} />
      <Route path="/b2b/analytics" element={<ProtectedRoute requiredAccountType="b2b"><B2BAnalyticsOverviewPage /></ProtectedRoute>} />
      <Route path="/b2b/exports" element={<ProtectedRoute requiredAccountType="b2b"><B2BExportsPage /></ProtectedRoute>} />
      <Route path="/b2b/resumes/:resumeId" element={<ProtectedRoute requiredAccountType="b2b"><B2BResumeDetailsPage /></ProtectedRoute>} />
      <Route path="/b2b/settings" element={<ProtectedRoute requiredAccountType="b2b"><B2BSettingsPage /></ProtectedRoute>} />

      <Route path="*" element={<PublicLayout><NotFoundPage /></PublicLayout>} />
    </Routes>
  );
}

export default App;
