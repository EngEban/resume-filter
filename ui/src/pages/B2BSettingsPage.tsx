import { useEffect, useState } from 'react';
import B2BShell from '../components/B2BShell';
import { useAuth } from '@/contexts/AuthContext';
import { b2bApi, APIError, type LLMSettings } from '@/lib/api';
import { BORDER, TEXT_MUTED } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';

export default function B2BSettingsPage() {
  const { user } = useAuth();
  const [current, setCurrent] = useState<LLMSettings | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoadState('loading');
      try {
        const settings = await b2bApi.getLLMSettings();
        if (!active) return;
        setCurrent(settings);
        setLoadState('ready');
      } catch (err) {
        if (!active) return;
        if (err instanceof APIError && err.status === 401) return;
        setLoadState('error');
      }
    }

    void load();
    return () => { active = false; };
  }, [refreshKey]);

  if (loadState === 'loading') {
    return (
      <B2BShell>
        <div className="space-y-4">
          <div className="h-10 w-64 skeleton" />
          <div className="h-40 skeleton" />
          <div className="h-72 skeleton" />
        </div>
      </B2BShell>
    );
  }

  if (loadState === 'error' || !current) {
    return (
      <B2BShell>
        <div className="py-24 text-center">
          <h1 className="text-2xl font-bold text-ink-900">Unable to load settings</h1>
          <button
            type="button"
            onClick={() => setRefreshKey((value) => value + 1)}
            className="btn btn-primary mt-6"
          >
            Try Again
          </button>
        </div>
      </B2BShell>
    );
  }

  return (
    <B2BShell>
      <div className="page-enter max-w-4xl space-y-8">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
            Workspace administration
          </p>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900">Organization Settings</h1>
          <p className="text-ink-600">Manage your workspace and platform-managed AI access.</p>
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

        <section className="rounded-2xl border bg-white p-6" style={{ borderColor: BORDER }}>
          <div className="flex items-start justify-between gap-4 border-b pb-4" style={{ borderColor: BORDER }}>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Central AI service</p>
              <h2 className="mt-1 text-xl font-bold text-ink-900">Platform-managed LLM</h2>
              <p className="mt-1 text-sm text-ink-500">
                AI requests use the platform provider and credentials. Organizations cannot add keys or change routing.
              </p>
            </div>
            <span className="badge badge-info">Platform Managed</span>
          </div>

          <div className="grid gap-4 pt-4 sm:grid-cols-2">
            <InfoTile label="Provider" value={current.provider} />
            <InfoTile label="Model" value={current.model} />
            <InfoTile label="Credentials" value="Managed by platform" />
            <InfoTile label="Endpoint" value="Managed server-side" />
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
      <dd className="break-all text-sm font-medium capitalize text-ink-900">{value}</dd>
    </div>
  );
}

function InfoTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border bg-ink-50 px-4 py-3" style={{ borderColor: BORDER }}>
      <p className="text-xs" style={{ color: TEXT_MUTED }}>{label}</p>
      <p className="mt-1 truncate text-sm font-semibold text-ink-900">{value}</p>
    </div>
  );
}
