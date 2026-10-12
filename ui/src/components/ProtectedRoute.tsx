// ============================================================
// src/components/ProtectedRoute.tsx
// Guards routes — checks auth + account type.
// ============================================================
import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { FullPageLoading } from './FullPageLoading';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredAccountType?: 'b2c' | 'b2b';
}

export function ProtectedRoute({
  children,
  requiredAccountType,
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <FullPageLoading />;
  }

  if (!isAuthenticated || !user) {
    return (
      <Navigate to="/login" replace state={{ from: location.pathname }} />
    );
  }

  if (requiredAccountType && user.account_type !== requiredAccountType) {
    const fallback =
      user.account_type === 'b2b' ? '/b2b/batches' : '/dashboard';
    return <Navigate to={fallback} replace />;
  }

  return <>{children}</>;
}