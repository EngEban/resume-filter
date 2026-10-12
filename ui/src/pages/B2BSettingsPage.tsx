import { useEffect, useMemo, useState } from 'react';
import B2BShell from '../components/B2BShell';
import { useAuth } from '@/contexts/AuthContext';
import { b2bApi, APIError, type LLMSettings, type ProvidersList } from '@/lib/api';
import { BORDER, DANGER, SUCCESS, TEXT_MUTED } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';

export default function B2BSettingsPage() {
  const { user } = useAuth();
  const [current, setCurrent] = useState<LLMSettings | null>(null);
  const [providers, setProviders] = useState<ProvidersList | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');

  const [provider, setProvider] = useState('');
  const [model, setModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [baseUrl, setBaseUrl] = useState('');

  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [removingKey, setRemovingKey] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoadState('loading');
      try {
        const [settings, list] = await Promise.all([
          b2bApi.getLLMSettings(),
          b2bApi.listProviders(),
        ]);
        if (!active) return;
        setCurrent(settings);
        setProviders(list);
        setProvider(settings.provider);
        setModel(settings.model);
        setBaseUrl(settings.base_url ?? '');
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

  const providerInfo = useMemo(
    () => providers?.providers.find((p) => p.provider === provider),
    [provider, providers],
  );

  const modelOptions = useMemo(() => {
    const list = providerInfo?.models ?? [];
    return model && !list.includes(model) ? [model, ...list] : list;
  }, [model, providerInfo]);

  const canManage = user?.role === 'owner' || user?.role === 'admin';

  function handleProviderChange(next: string) {
    setProvider(next);
    const info = providers?.providers.find((p) => p.provider === next);
    setModel(info?.models[0] ?? '');
    setFeedback(null);
  }

  function validate(): string {
    if (!model.trim()) return 'Select a model.';
    if (provider !== 'ollama' && !apiKey.trim()) return 'Enter an API key.';
    return '';
  }

  async function testConnection() {
    const err = validate();
    if (err) { setFeedback({ type: 'error', message: err }); return; }
    setTesting(true);
    setFeedback(null);
    try {
      const result = await b2bApi.testLLMConnection(
        provider,
        model,
        apiKey.trim() || undefined,
        baseUrl.trim() || undefined,
      );
      if (result.success) {
        setFeedback({
          type: 'success',
          message: result.latency_ms ? `Connection successful · ${result.latency_ms} ms` : 'Connection successful.',
        });
      } else {
        setFeedback({ type: 'error', message: result.message || 'Connection failed.' });
      }
    } catch (e) {
      setFeedback({ type: 'error', message: e instanceof APIError ? e.message : 'Connection failed.' });
    } finally {
      setTesting(false);
    }
  }

  async function save() {
    if (!canManage) {
      setFeedback({ type: 'error', message: 'Only owners and admins can change settings.' });
      return;
    }
    const err = validate();
    if (err) { setFeedback({ type: 'error', message: err }); return; }
    setSaving(true);
    setFeedback(null);
    try {
      const updated = await b2bApi.updateLLMSettings(
        provider,
        model,
        apiKey.trim() || undefined,
        baseUrl.trim() || undefined,
      );
      setCurrent(updated);
      setApiKey('');
      setFeedback({ type: 'success', message: 'Settings saved.' });
    } catch (e) {
      setFeedback({ type: 'error', message: e instanceof APIError ? e.message : 'Unable to save.' });
    } finally {
      setSaving(false);
    }
  }

  async function removeKey() {
    if (!canManage || removingKey) return;
    if (!window.confirm('Revert to platform default?')) return;
    setRemovingKey(true);
    setFeedback(null);
    try {
      await b2bApi.deleteLLMSettings();
      setApiKey('');
      setFeedback({ type: 'success', message: 'Reverted to platform default.' });
      setRefreshKey((v) => v + 1);
    } catch (e) {
      setFeedback({ type: 'error', message: e instanceof APIError ? e.message : 'Unable to revert.' });
    } finally {
      setRemovingKey(false);
    }
  }

  if (loadState === 'loading') {
    return (
      <B2BShell>
        <div className="space-y-4">
          <div className="h-10 w-64 skeleton" />
          <div className="h-40 skeleton" />
          <div className="h-96 skeleton" />
        </div>
      </B2BShell>
    );
  }

  if (loadState === 'error' || !current || !providers) {
    return (
      <B2BShell>
        <div className="py-24 text-center">
          <h1 className="text-2xl font-bold text-ink-900">Unable to load settings</h1>
          <button
            type="button"
            onClick={() => setRefreshKey((v) => v + 1)}
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
        {/* Header */}
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
            Workspace administration
          </p>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900">Organization Settings</h1>
          <p className="text-ink-600">Manage your workspace and AI configuration.</p>
        </div>

        {/* Account */}
        <section className="rounded-2xl border bg-white p-6" style={{ borderColor: BORDER }}>
          <div className="pb-4 border-b" style={{ borderColor: BORDER }}>
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

        {/* Current config */}
        <section className="rounded-2xl border bg-white p-6" style={{ borderColor: BORDER }}>
          <div className="flex items-center justify-between gap-4 pb-4 border-b" style={{ borderColor: BORDER }}>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Current routing</p>
              <h2 className="mt-1 text-xl font-bold text-ink-900">LLM configuration</h2>
            </div>
            <span className={`badge ${current.source === 'tenant' ? 'badge-success' : 'badge-info'}`}>
              {current.source === 'tenant' ? 'Workspace Key' : 'Platform Default'}
            </span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 pt-4">
            <InfoTile label="Provider" value={current.provider} />
            <InfoTile label="Model" value={current.model} />
            <InfoTile label="Custom key" value={current.has_custom_key ? 'Configured' : 'Not configured'} />
            <InfoTile label="Base URL" value={current.base_url || 'Default'} />
          </div>

          {current.has_custom_key && (
            <button
              type="button"
              onClick={() => void removeKey()}
              disabled={removingKey || !canManage}
              className="mt-5 text-sm font-medium transition disabled:opacity-50"
              style={{ color: DANGER }}
            >
              {removingKey ? 'Reverting…' : 'Revert to platform default'}
            </button>
          )}
        </section>

        {/* BYOK config */}
        <section className="rounded-2xl border bg-white p-6" style={{ borderColor: BORDER }}>
          <div className="flex items-start justify-between gap-4 pb-4 border-b" style={{ borderColor: BORDER }}>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">BYOK configuration</p>
              <h2 className="mt-1 text-xl font-bold text-ink-900">Configure a provider</h2>
              <p className="mt-1 text-sm text-ink-500">
                Use the platform default or connect your own provider.
              </p>
            </div>
            {!canManage && (
              <span className="text-xs" style={{ color: TEXT_MUTED }}>Read-only</span>
            )}
          </div>

          <div className="grid gap-5 md:grid-cols-2 pt-5">
            <div className="space-y-1.5">
              <label className="label" htmlFor="provider">Provider</label>
              <select
                id="provider"
                value={provider}
                onChange={(e) => handleProviderChange(e.target.value)}
                disabled={!canManage}
                className="input"
              >
                {providers.providers.map((p) => (
                  <option key={p.provider} value={p.provider}>{p.provider}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="label" htmlFor="model">Model</label>
              <select
                id="model"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                disabled={!canManage}
                className="input"
              >
                {modelOptions.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
                {modelOptions.length === 0 && <option value={model}>{model}</option>}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="label" htmlFor="api-key">
                API Key {providerInfo?.requires_api_key && <span className="text-brand-600">*</span>}
              </label>
              <input
                id="api-key"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                disabled={!canManage}
                placeholder={
                  current.has_custom_key
                    ? 'Enter a replacement key'
                    : providerInfo?.requires_api_key
                      ? 'Required for this provider'
                      : 'Optional for Ollama'
                }
                className="input"
              />
            </div>

            <div className="space-y-1.5">
              <label className="label" htmlFor="base-url">
                Base URL{' '}
                <span className="text-xs font-normal" style={{ color: TEXT_MUTED }}>
                  {providerInfo?.supports_base_url ? '(optional)' : '(not required)'}
                </span>
              </label>
              <input
                id="base-url"
                type="text"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                disabled={!canManage || !providerInfo?.supports_base_url}
                placeholder={providerInfo?.supports_base_url ? 'https://...' : 'Not used'}
                className="input"
              />
            </div>
          </div>

          {feedback && (
            <div
              role="status"
              className="mt-5 rounded-xl border px-4 py-3 text-sm"
              style={{
                borderColor: feedback.type === 'success' ? '#A7F3D0' : '#FECACA',
                background: feedback.type === 'success' ? '#ECFDF5' : '#FEF2F2',
                color: feedback.type === 'success' ? SUCCESS : DANGER,
              }}
            >
              {feedback.message}
            </div>
          )}

          <div className="mt-6 flex flex-col-reverse gap-3 pt-5 border-t sm:flex-row sm:justify-end" style={{ borderColor: BORDER }}>
            <button
              type="button"
              onClick={() => void testConnection()}
              disabled={testing || saving || !canManage}
              className="btn btn-secondary"
            >
              {testing ? 'Testing…' : 'Test Connection'}
            </button>
            <button
              type="button"
              onClick={() => void save()}
              disabled={saving || testing || !canManage}
              className="btn btn-primary"
            >
              {saving ? 'Saving…' : 'Save Settings'}
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
      <dd className="text-sm font-medium capitalize text-ink-900 break-all">{value}</dd>
    </div>
  );
}

function InfoTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border bg-ink-50 px-4 py-3" style={{ borderColor: BORDER }}>
      <p className="text-xs" style={{ color: TEXT_MUTED }}>{label}</p>
      <p className="mt-1 text-sm font-semibold text-ink-900 truncate">{value}</p>
    </div>
  );
}
