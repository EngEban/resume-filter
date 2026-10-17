import B2BShell from '../components/B2BShell';
import { useAuth } from '@/contexts/AuthContext';
import { BORDER, TEXT_MUTED } from '@/theme';

export default function B2BSettingsPage() {
  const { user, logout } = useAuth();

  // تنسيق كلمة Role
  const formattedRole = user?.role 
    ? user.role.charAt(0).toUpperCase() + user.role.slice(1) 
    : 'Owner';

  // في نظامنا، الـ display_name للمؤسسة يحمل اسم المؤسسة (مثلاً TechNova Solutions)
  const organizationName = user?.display_name || 'Your Organization';

  return (
    <B2BShell>
      <div className="page-enter max-w-4xl space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
            Workspace administration
          </p>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900">Organization Settings</h1>
          <p className="text-ink-600">Manage your organization profile, access, and security.</p>
        </div>

        {/* 1. Organization Profile */}
        <section className="rounded-2xl border bg-white p-6 shadow-soft-sm" style={{ borderColor: BORDER }}>
          <div className="border-b pb-4" style={{ borderColor: BORDER }}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Profile</p>
            <h2 className="mt-1 text-xl font-bold text-ink-900">Organization details</h2>
          </div>
          <dl className="divide-y" style={{ borderColor: BORDER }}>
            <Row label="Organization name" value={organizationName} />
            <Row label="Workspace ID" value={user?.tenant_id ? user.tenant_id.slice(0, 8) : '—'} />
          </dl>
        </section>

        {/* 2. Workspace Access */}
        <section className="rounded-2xl border bg-white p-6 shadow-soft-sm" style={{ borderColor: BORDER }}>
          <div className="border-b pb-4" style={{ borderColor: BORDER }}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Account</p>
            <h2 className="mt-1 text-xl font-bold text-ink-900">Your workspace access</h2>
          </div>
          <dl className="divide-y" style={{ borderColor: BORDER }}>
            <Row label="Email address" value={user?.email ?? '—'} />
            <Row label="Role" value={formattedRole} />
            <Row label="Account type" value="Organization" />
          </dl>
        </section>

        {/* 3. Security */}
        <section className="rounded-2xl border bg-white p-6 shadow-soft-sm" style={{ borderColor: BORDER }}>
          <div className="border-b pb-4" style={{ borderColor: BORDER }}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Security</p>
            <h2 className="mt-1 text-xl font-bold text-ink-900">Account security</h2>
          </div>
          <div className="pt-4">
            <p className="text-sm text-ink-600">
              Your organization workspace is protected by TalentScope multi-tenant authentication and Row-Level Security (RLS).
            </p>
          </div>
        </section>

        {/* 4. Actions */}
        <section className="rounded-2xl border bg-white p-6 shadow-soft-sm" style={{ borderColor: BORDER }}>
          <div className="border-b pb-4" style={{ borderColor: BORDER }}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Actions</p>
            <h2 className="mt-1 text-xl font-bold text-ink-900">Sign out</h2>
          </div>
          <div className="flex flex-col gap-4 pt-6 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-ink-600">End your current session on this device.</p>
            <button
              onClick={logout}
              className="inline-flex h-10 items-center justify-center rounded-xl bg-red-600 px-6 text-sm font-semibold text-white transition-colors hover:bg-red-700"
            >
              Sign Out
            </button>
          </div>
        </section>
      </div>
    </B2BShell>
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