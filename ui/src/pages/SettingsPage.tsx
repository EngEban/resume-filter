import { useAuth } from '@/contexts/AuthContext';
import { BORDER, TEXT_MUTED } from '@/theme';

export default function SettingsPage() {
  const { user, logout } = useAuth();

  const formattedRole = user?.role 
    ? user.role.charAt(0).toUpperCase() + user.role.slice(1) 
    : 'Member';

  return (
    <div className="page-enter max-w-4xl space-y-8">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
          Account
        </p>
        <h1 className="text-4xl font-bold tracking-tight text-ink-900">Settings</h1>
        <p className="text-ink-600">Manage your account and preferences.</p>
      </div>

      <section className="rounded-2xl border bg-white p-6" style={{ borderColor: BORDER }}>
        <div className="border-b pb-4" style={{ borderColor: BORDER }}>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Account</p>
          <h2 className="mt-1 text-xl font-bold text-ink-900">Profile information</h2>
        </div>
        <dl className="divide-y" style={{ borderColor: BORDER }}>
          <Row label="Email" value={user?.email ?? '—'} />
          <Row label="Account type" value={user?.account_type === 'b2b' ? 'Organization' : 'Individual'} />
          <Row label="Role" value={formattedRole} />
          <Row label="Status" value={user?.is_active ? 'Active' : 'Inactive'} />
        </dl>
      </section>

      <section className="rounded-2xl border bg-white p-6" style={{ borderColor: BORDER }}>
        <div className="border-b pb-4" style={{ borderColor: BORDER }}>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Security</p>
          <h2 className="mt-1 text-xl font-bold text-ink-900">Account security</h2>
        </div>
        <div className="pt-4">
          <p className="text-sm text-ink-600">
            Your account is protected by TalentScope authentication.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border bg-white p-6" style={{ borderColor: BORDER }}>
        <div className="border-b pb-4" style={{ borderColor: BORDER }}>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Actions</p>
          <h2 className="mt-1 text-xl font-bold text-ink-900">Sign out</h2>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-6">
          <p className="text-sm text-ink-600">End your current session on this device.</p>
          <button
            onClick={logout}
            className="btn bg-red-600 text-white hover:bg-red-700 h-10 px-6 rounded-xl font-semibold text-sm transition-colors"
          >
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
      <dd className="break-all text-sm font-medium text-ink-900">{value}</dd>
    </div>
  );
}