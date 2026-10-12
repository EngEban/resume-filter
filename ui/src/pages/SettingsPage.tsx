import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { BORDER, TEXT_MUTED, TEXT_PRIMARY } from '@/theme';

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function signOut() {
    logout();
    navigate('/login', { replace: true });
  }

  return (
    <div className="page-enter max-w-3xl space-y-8">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Account</p>
        <h1 className="text-4xl font-bold tracking-tight text-ink-900">Settings</h1>
        <p className="text-ink-600">Manage your account and preferences.</p>
      </div>

      {/* Profile */}
      <section className="rounded-2xl border bg-white p-6 hover-lift" style={{ borderColor: BORDER }}>
        <div className="pb-4 border-b" style={{ borderColor: BORDER }}>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Account</p>
          <h2 className="mt-1 text-xl font-bold text-ink-900">Profile information</h2>
        </div>
        <dl className="divide-y" style={{ borderColor: BORDER }}>
          <Row label="Email" value={user?.email ?? '—'} />
          <Row label="Account type" value={user?.account_type === 'b2b' ? 'Organization' : 'Individual'} />
          <Row label="Role" value={user?.role ?? 'Member'} />
          <Row label="Status" value={user?.is_active ? 'Active' : 'Disabled'} />
        </dl>
      </section>

      {/* Security */}
      <section className="rounded-2xl border bg-white p-6 hover-lift" style={{ borderColor: BORDER }}>
        <div className="pb-4 border-b" style={{ borderColor: BORDER }}>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Security</p>
          <h2 className="mt-1 text-xl font-bold text-ink-900">Account security</h2>
        </div>
        <p className="pt-4 text-sm text-ink-600 leading-6">
          Your account is protected by TalentScope authentication.
        </p>
      </section>

      {/* Sign out */}
      <section className="rounded-2xl border bg-white p-6 hover-lift" style={{ borderColor: BORDER }}>
        <div className="pb-4 border-b" style={{ borderColor: BORDER }}>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Actions</p>
          <h2 className="mt-1 text-xl font-bold text-ink-900">Sign out</h2>
        </div>
        <div className="pt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-ink-600">End your current session on this device.</p>
          <button type="button" onClick={signOut} className="btn btn-danger">
            Sign Out
          </button>
        </div>
      </section>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:justify-between">
      <dt className="text-sm" style={{ color: TEXT_MUTED }}>{label}</dt>
      <dd className="text-sm font-medium break-all" style={{ color: TEXT_PRIMARY }}>{value}</dd>
    </div>
  );
}
