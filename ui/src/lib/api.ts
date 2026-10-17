// ============================================================
// src/lib/api.ts
// Centralized API client for TalentScope.
// ============================================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';
const TOKEN_KEY = 'access_token';
const USER_KEY = 'user';

export interface UserProfile {
  id: string;
  email: string;
  account_type: 'b2c' | 'b2b';
  role?: string;
  tenant_id?: string | null;
  is_active: boolean;
  is_verified: boolean;
  display_name: string;
}

export class APIError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

export const auth = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  getUser(): UserProfile | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as UserProfile;
    } catch {
      return null;
    }
  },

  save(token: string, user: UserProfile): void {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  clear(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

async function request<T>(
  method: string,
  path: string,
  options: {
    body?: unknown;
    formData?: FormData;
    urlEncoded?: URLSearchParams;
    requiresAuth?: boolean;
  } = {},
): Promise<T> {
  const { body, formData, urlEncoded, requiresAuth = true } = options;

  const headers: Record<string, string> = {
    Accept: 'application/json',
  };

  if (requiresAuth) {
    const token = auth.getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let payload: BodyInit | undefined;

  if (formData) {
    payload = formData;
  } else if (urlEncoded) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    payload = urlEncoded;
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: payload,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type') ?? '';
  const isJson = contentType.includes('application/json');

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    if (isJson) {
      const error = (await response.json().catch(() => null)) as
        | { detail?: string; message?: string }
        | null;
      message = error?.message ?? error?.detail ?? message;
    }
    throw new APIError(response.status, message);
  }

  if (isJson) {
    return (await response.json()) as T;
  }

  return (await response.text()) as unknown as T;
}

export async function fetchBlob(
  path: string,
): Promise<{ blob: Blob; filename: string }> {
  const token = auth.getToken();
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE_URL}${path}`, { headers });

  if (!response.ok) {
    throw new APIError(response.status, 'Download failed');
  }

  const disposition = response.headers.get('content-disposition') ?? '';
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match?.[1] ?? 'download';

  return { blob: await response.blob(), filename };
}

// ============================================================
// Auth endpoints
// ============================================================
export const authApi = {
  async login(
    email: string,
    password: string,
  ): Promise<{ access_token: string }> {
    return request<{ access_token: string; token_type: string }>(
      'POST',
      '/api/v1/auth/login',
      {
        urlEncoded: new URLSearchParams({ username: email, password }),
        requiresAuth: false,
      },
    );
  },

  async me(): Promise<UserProfile> {
    return request<UserProfile>('GET', '/api/v1/auth/me');
  },

  async registerB2C(
    email: string,
    password: string,
  ): Promise<{ message: string; email: string }> {
    return request<{ message: string; email: string }>(
      'POST',
      '/api/v1/auth/register/b2c',
      {
        body: { email, password, account_type: 'b2c' },
        requiresAuth: false,
      },
    );
  },

  async registerB2B(
    organization_name: string,
    organization_slug: string,
    email: string,
    password: string,
  ): Promise<{ message: string; email: string }> {
    return request<{ message: string; email: string }>(
      'POST',
      '/api/v1/auth/register/b2b',
      {
        body: { organization_name, organization_slug, email, password },
        requiresAuth: false,
      },
    );
  },

  async verifyEmail(token: string): Promise<{ message: string }> {
    return request<{ message: string }>(
      'GET',
      `/api/v1/auth/verify-email?token=${encodeURIComponent(token)}`,
      { requiresAuth: false },
    );
  },

  async resendVerification(email: string): Promise<{ message: string }> {
    return request<{ message: string }>(
      'POST',
      `/api/v1/auth/resend-verification?email=${encodeURIComponent(email)}`,
      { requiresAuth: false },
    );
  },

  googleLoginUrl(): string {
    const base = import.meta.env.VITE_API_BASE_URL ?? '';
    return `${base}/api/v1/auth/google/login`;
  },
};

// ============================================================
// B2C endpoints
// ============================================================
export interface AnalysisResponse {
  id: string;
  ats_score: number;
  level: 'excellent' | 'good' | 'average' | 'below_average' | 'weak';
  level_label: string;
  breakdown: Record<string, number>;
  matched_keywords: string[];
  missing_keywords: string[];
  suggestions: Array<{
    type: string;
    priority: 'high' | 'medium' | 'low';
    description: string;
    original?: string;
    suggestion?: string;
  }>;
  created_at: string;
}

export interface AnalysisHistoryItem {
  id: string;
  ats_score: number;
  breakdown: Record<string, number>;
  missing_keywords: string[];
  created_at: string;
}

export const b2cApi = {
  async analyze(file: File, jobDescription: string): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);

    return request<AnalysisResponse>('POST', '/api/v1/b2c/analyze', { formData });
  },

    async history(limit = 20): Promise<AnalysisHistoryItem[]> {
    return request<AnalysisHistoryItem[]>('GET', `/api/v1/b2c/history?limit=${limit}`);
  },

  async deleteAnalysis(id: string): Promise<{ message: string; id: string }> {
    return request<{ message: string; id: string }>(
      'DELETE',
      `/api/v1/b2c/history/${id}`,
    );
  },

  async clearHistory(): Promise<{ message: string; deleted_count: number }> {
    return request<{ message: string; deleted_count: number }>(
      'DELETE',
      '/api/v1/b2c/history',
    );
  },
};

// ============================================================
// B2B endpoints
// ============================================================
export interface Batch {
  id: string;
  tenant_id: string;
  job_title: string;
  status: string;
  total_resumes: number;
  completed: number;
  failed: number;
  created_at: string;
  completed_at: string | null;
}

export interface Resume {
  id: string;
  file_name: string;
  candidate_name: string | null;
  candidate_email: string | null;
  candidate_phone?: string | null;
  ats_score: number | null;
  status: string;
  score_breakdown?: Record<string, number> | null;
  missing_keywords?: string[];
  suggestions?: Array<Record<string, unknown>>;
  error_message?: string | null;
  created_at: string;
}

export interface BatchAnalytics {
  batch_id: string;
  job_title: string;
  status: string;
  total_resumes: number;
  completed: number;
  failed: number;
  pending: number;
  avg_score: number | null;
  median_score: number | null;
  min_score: number | null;
  max_score: number | null;
  score_distribution: Record<string, number>;
  top_missing_keywords: Array<{ keyword: string; count: number }>;
  completion_rate: number;
}

export interface TenantOverview {
  tenant_id: string;
  total_batches: number;
  total_resumes: number;
  total_completed: number;
  total_failed: number;
  avg_ats_score: number | null;
  score_distribution: Record<string, number>;
  top_missing_keywords: Array<{ keyword: string; count: number }>;
  recent_batches: Batch[];
}

export const b2bApi = {
  async listBatches(params?: { search?: string; status?: string; limit?: number; offset?: number }): Promise<Batch[]> {
    const query = new URLSearchParams();
    if (params?.search) query.set('search', params.search);
    if (params?.status) query.set('status', params.status);
    if (params?.limit) query.set('limit', String(params.limit));
    if (params?.offset) query.set('offset', String(params.offset));
    const qs = query.toString();
    return request<Batch[]>('GET', `/api/v1/b2b/batches${qs ? '?' + qs : ''}`);
  },

  async getBatch(id: string): Promise<Batch> {
    return request<Batch>('GET', `/api/v1/b2b/batches/${id}`);
  },

  async createBatch(
    jobTitle: string,
    jobDescription: string,
    files: File[],
    jobRequirements?: string,
  ): Promise<Batch> {
    const formData = new FormData();
    formData.append('job_title', jobTitle);
    formData.append('job_description', jobDescription);
    if (jobRequirements) formData.append('job_requirements', jobRequirements);
    files.forEach((file) => formData.append('files', file));
    return request<Batch>('POST', '/api/v1/b2b/batches', { formData });
  },

  async listResumes(
    batchId: string,
    params?: { search?: string; status?: string; min_score?: number; sort?: string },
  ): Promise<Resume[]> {
    const query = new URLSearchParams();
    if (params?.search) query.set('search', params.search);
    if (params?.status) query.set('status', params.status);
    if (params?.min_score !== undefined) query.set('min_score', String(params.min_score));
    if (params?.sort) query.set('sort', params.sort);
    const qs = query.toString();
    return request<Resume[]>('GET', `/api/v1/b2b/batches/${batchId}/resumes${qs ? '?' + qs : ''}`);
  },

  async getResume(resumeId: string): Promise<Resume> {
    return request<Resume>('GET', `/api/v1/b2b/resumes/${resumeId}`);
  },

  async reprocessBatch(batchId: string): Promise<Batch> {
    return request<Batch>('POST', `/api/v1/b2b/batches/${batchId}/reprocess`);
  },

  async getAnalytics(batchId: string): Promise<BatchAnalytics> {
    return request<BatchAnalytics>('GET', `/api/v1/b2b/analytics/batches/${batchId}`);
  },

  async getOverview(): Promise<TenantOverview> {
    return request<TenantOverview>('GET', '/api/v1/b2b/analytics/overview');
  },

  async compare(batchId: string, limit = 5): Promise<{ candidates: Resume[] }> {
    return request('GET', `/api/v1/b2b/resumes/compare?batch_id=${batchId}&limit=${limit}`);
  },

  async exportBatchExcel(batchId: string) {
    return fetchBlob(`/api/v1/b2b/batches/${batchId}/export.xlsx`);
  },

  async exportBatchPdf(batchId: string) {
    return fetchBlob(`/api/v1/b2b/batches/${batchId}/export.pdf`);
  },

  async exportResumePdf(resumeId: string) {
    return fetchBlob(`/api/v1/b2b/resumes/${resumeId}/report.pdf`);
  },

  async exportComparison(batchId: string, limit = 10) {
    return fetchBlob(`/api/v1/b2b/resumes/compare/export.xlsx?batch_id=${batchId}&limit=${limit}`);
  },
    async deleteBatch(id: string): Promise<{ message: string; id: string; deleted_resumes: number }> {
    return request('DELETE', `/api/v1/b2b/batches/${id}`);
  },

  async clearAllBatches(): Promise<{ message: string; deleted_batches: number; deleted_resumes: number }> {
    return request('DELETE', '/api/v1/b2b/batches');
  },
};
