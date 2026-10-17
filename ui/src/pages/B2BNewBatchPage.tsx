import { useState, type ChangeEvent, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { APIError, b2bApi } from '@/lib/api';
import { DANGER } from '@/theme';

const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const MAX_BATCH_SIZE = 500;

export default function B2BNewBatchPage() {
  const navigate = useNavigate();
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobRequirements, setJobRequirements] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [createError, setCreateError] = useState('');
  const [creating, setCreating] = useState(false);

  function handleFiles(e: ChangeEvent<HTMLInputElement>) {
    const selected = Array.from(e.target.files ?? []);
    setCreateError('');
    if (selected.length > MAX_BATCH_SIZE) {
      setCreateError(`Max ${MAX_BATCH_SIZE} files per batch.`);
      setFiles(selected.slice(0, MAX_BATCH_SIZE));
      return;
    }
    const invalid = selected.find((f) => {
      const ext = f.name.toLowerCase().split('.').pop();
      return !['pdf', 'docx'].includes(ext ?? '') || f.size === 0 || f.size > MAX_FILE_SIZE_BYTES;
    });
    if (invalid) {
      setCreateError(`${invalid.name} must be a PDF/DOCX under ${MAX_FILE_SIZE_MB} MB.`);
      setFiles([]);
      return;
    }
    setFiles(selected);
  }

  async function submitBatch(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!jobTitle.trim() || jobDescription.trim().length < 20 || files.length === 0) {
      setCreateError('Add a title, description (20+ chars), and one or more files.');
      return;
    }
    setCreating(true);
    setCreateError('');
    try {
      await b2bApi.createBatch(jobTitle.trim(), jobDescription.trim(), files, jobRequirements.trim() || undefined);
      navigate('/b2b/batches', { replace: true });
    } catch (err) {
      setCreateError(err instanceof APIError ? err.message : 'Unable to create batch.');
    } finally {
      setCreating(false);
    }
  }

  const totalSizeMb = files.reduce((sum, file) => sum + file.size, 0) / (1024 * 1024);
  const formInvalid = !jobTitle.trim() || jobDescription.trim().length < 20 || files.length === 0;

  return (
    <B2BShell>
      <div className="page-enter space-y-8">
        <Link to="/b2b/batches" className="inline-flex items-center gap-2 text-sm font-semibold text-ink-500 hover:text-brand-600">
          <span aria-hidden="true"><i className="fa-solid fa-arrow-left" /></span> Back to Batches
        </Link>

        <header className="max-w-3xl space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Organization workspace</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-900">Create a New Batch</h1>
          <p className="text-ink-600">Set up a role, upload resumes, and let TalentScope surface the strongest signals.</p>
        </header>

        <form onSubmit={submitBatch} noValidate className="space-y-6">
          <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
            <section aria-labelledby="job-details-heading" className="rounded-2xl border border-ink-100 bg-white/80 p-6 shadow-soft-md backdrop-blur-sm sm:p-8">
              <div className="flex items-center gap-3 border-b border-ink-100 pb-5">
                <span className="grid h-9 w-9 place-items-center rounded-xl bg-ink-100 text-xs font-bold text-ink-600">01</span>
                <div>
                  <h2 id="job-details-heading" className="text-xl font-bold text-ink-900">Job Details</h2>
                  <p className="mt-0.5 text-sm text-ink-500">Tell us what you are hiring for.</p>
                </div>
              </div>

              <div className="mt-6 space-y-5">
                <div className="space-y-1.5">
                  <label className="label" htmlFor="job-title">Job Title <span className="text-brand-600">*</span></label>
                  <input id="job-title" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} className={`input ${!jobTitle.trim() && createError ? 'input-error' : ''}`} placeholder="e.g. Senior Product Designer" required aria-invalid={!jobTitle.trim() && Boolean(createError)} />
                  {!jobTitle.trim() && createError && <p className="text-xs text-red-600">Add a job title to continue.</p>}
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between gap-3">
                    <label className="label mb-0" htmlFor="job-desc">Job Description <span className="text-brand-600">*</span></label>
                    <span className={`text-xs tabular-nums ${jobDescription.trim().length < 20 && createError ? 'text-red-600' : 'text-ink-500'}`}>{jobDescription.length} / 20 min</span>
                  </div>
                  <textarea id="job-desc" value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} rows={5} minLength={20} className={`input resize-y ${jobDescription.trim().length < 20 && createError ? 'input-error' : ''}`} placeholder="Describe the role, team, responsibilities, and what success looks like." required aria-invalid={jobDescription.trim().length < 20 && Boolean(createError)} />
                  <p className={`text-xs ${jobDescription.trim().length < 20 && createError ? 'text-red-600' : 'text-ink-500'}`}>Use at least 20 characters so the screening model has enough context.</p>
                </div>

                <div className="space-y-1.5">
                  <label className="label" htmlFor="job-reqs">Job Requirements <span className="font-normal text-ink-400">(optional)</span></label>
                  <textarea id="job-reqs" value={jobRequirements} onChange={(e) => setJobRequirements(e.target.value)} rows={3} className="input resize-y" placeholder="Optional skills, qualifications, or must-have experience." />
                </div>
              </div>
            </section>

            <section aria-labelledby="resume-upload-heading" className="rounded-2xl border border-ink-100 bg-white/80 p-6 shadow-soft-md backdrop-blur-sm sm:p-8">
              <div className="flex items-center gap-3 border-b border-ink-100 pb-5">
                <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand-50 text-xs font-bold text-brand-600">02</span>
                <div>
                  <h2 id="resume-upload-heading" className="text-xl font-bold text-ink-900">Resume Upload</h2>
                  <p className="mt-0.5 text-sm text-ink-500">Add resumes for AI screening.</p>
                </div>
              </div>

              <div className="mt-6">
                {files.length === 0 ? (
                  <label
                    htmlFor="batch-files"
                    data-dragging="false"
                    onDragEnter={(e) => { e.preventDefault(); e.currentTarget.dataset.dragging = 'true'; }}
                    onDragOver={(e) => { e.preventDefault(); e.currentTarget.dataset.dragging = 'true'; }}
                    onDragLeave={(e) => { if (e.currentTarget === e.target) e.currentTarget.dataset.dragging = 'false'; }}
                    onDrop={(e) => { e.preventDefault(); e.currentTarget.dataset.dragging = 'false'; handleFiles({ target: { files: e.dataTransfer.files } } as unknown as ChangeEvent<HTMLInputElement>); }}
                    className={`group flex min-h-[220px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-ink-200 px-6 py-8 text-center transition duration-200 data-[dragging=true]:scale-[1.02] data-[dragging=true]:border-brand-500 data-[dragging=true]:bg-brand-50 data-[dragging=true]:shadow-lg ${!files.length && createError ? 'animate-glow-pulse border-brand-300' : ''}`}
                  >
                    <span className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-50 text-brand-600 transition duration-200 group-hover:scale-105 group-hover:bg-brand-100 group-data-[dragging=true]:scale-110 group-data-[dragging=true]:bg-brand-100" aria-hidden="true">
                      <svg width="25" height="25" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <path d="m17 8-5-5-5 5M12 3v12" />
                      </svg>
                    </span>
                    <span className="mt-4 text-base font-semibold text-ink-900">Drop resumes here or click to browse</span>
                    <span className="mt-1 text-sm text-ink-500">Select multiple PDF or DOCX files at once.</span>
                    <span className="mt-4 inline-flex items-center rounded-full bg-ink-100 px-3 py-1 text-xs font-medium text-ink-600">PDF · DOCX · Max {MAX_FILE_SIZE_MB} MB each</span>
                    <input id="batch-files" type="file" multiple accept=".pdf,.docx" onChange={handleFiles} className="sr-only" />
                  </label>
                ) : (
                  <div className="rounded-2xl border border-brand-100 bg-brand-50/40 p-3 animate-fade-in" aria-live="polite">
                    <div className="mb-3 flex items-center justify-between gap-3 px-2">
                      <div>
                        <p className="text-sm font-semibold text-ink-900">Selected resumes</p>
                        <p className="text-xs text-ink-500">Review files before creating the batch.</p>
                      </div>
                      <label htmlFor="batch-files" className="btn btn-secondary btn-sm cursor-pointer">Add more</label>
                    </div>
                    <input id="batch-files" type="file" multiple accept=".pdf,.docx" onChange={handleFiles} className="sr-only" />
                    <div className="max-h-72 space-y-2 overflow-y-auto pr-1">
                      {files.map((file) => (
                        <div key={`${file.name}-${file.lastModified}`} className="flex items-center gap-3 rounded-xl border border-ink-200/80 bg-white px-3 py-2.5 shadow-sm animate-fade-in-down">
                          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-emerald-50 text-[10px] font-bold uppercase text-emerald-700" aria-hidden="true">{file.name.toLowerCase().endsWith('.pdf') ? 'PDF' : 'DOC'}</span>
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-medium text-ink-800">{file.name}</p>
                            <p className="text-xs text-ink-500">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                          </div>
                          <button type="button" onClick={() => setFiles((current) => current.filter((item) => item.name !== file.name))} className="shrink-0 rounded-lg px-2 py-1.5 text-xs font-semibold text-ink-500 transition hover:bg-red-50 hover:text-red-600" aria-label={`Remove ${file.name}`}>Remove</button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </section>
          </div>

          {files.length > 0 && (
            <section aria-label="Batch summary" className="rounded-2xl border border-ink-100 bg-white/80 p-5 shadow-soft-md backdrop-blur-sm sm:px-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">03 · Summary</p>
                  <p className="mt-1 text-sm font-medium text-ink-700">{files.length} {files.length === 1 ? 'file' : 'files'} selected</p>
                </div>
                <p className="text-sm font-semibold text-ink-900 tabular-nums">Total {totalSizeMb.toFixed(2)} MB</p>
              </div>
            </section>
          )}

          {createError && (
            <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm" style={{ color: DANGER }}>{createError}</div>
          )}

          <div className="flex flex-col gap-3 rounded-2xl border border-ink-100 bg-white/80 p-5 shadow-soft-md backdrop-blur-sm sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <p className="text-xs text-ink-500">You can add up to {MAX_BATCH_SIZE} files.</p>
            <div className="flex flex-col-reverse gap-2 sm:flex-row">
              <Link to="/b2b/batches" className="btn btn-ghost">Cancel</Link>
              <button type="submit" disabled={creating || formInvalid} className="btn btn-primary min-w-36 hover-lift">
                {creating ? <><span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" /> Creating…</> : 'Create Batch'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </B2BShell>
  );
}
