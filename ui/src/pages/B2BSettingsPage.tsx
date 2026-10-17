import B2BShell from '../components/B2BShell';
import { useAuth } from '@/contexts/AuthContext';
import { BORDER, TEXT_MUTED } from '@/theme';

export default function B2BSettingsPage() {
  const { user } = useAuth();

  return (
    <B2BShell>
      <div className="page-enter max-w-4xl space-y-8">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
            Workspace administration
          </p>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900">Organization Settings</h1>
          <p className="text-ink-600">Manage your workspace access and account details.</p>
        </div>

        <section className="rounded-2xl border bg-white p-6" style={{ borderColor: BORDER }}>
          <div className="border-b pb-4" style={{ borderColor: BORDER }}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Account</p>
            <h2 className="mt-1 text-xl font-bold text-ink-900">Workspace access</h2>
          </div>
          <dl className="divide-y" style={{ borderColor: BORDER }}>
            <Row label="Email" value={user?.email ?? '—'} />
            <Row label="Role" value={user?.role ?? 'Member'} />
            <Row label="Account type" value={user?.account_type === 'b2b' ? 'Organization' : 'Individual'} />
            <Row label="Workspace" value={user?.tenant_id ? 'Organization tenant' : 'Not available'} />
          </dl>
        </section>
      </div>
    </B2BShell>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:justify-between">
      <dt className="text-sm" style={{ color: TEXT_MUTED }}>{label}</dt>
      <dd className="break-all text-sm font-medium capitalize text-ink-900">{value}</dd>
    </div>
  );
}
