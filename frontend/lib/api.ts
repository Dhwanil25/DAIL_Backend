// API base URL — points to the FastAPI backend
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

import type {
    PaginatedResponse,
    CaseResponse,
    CaseCreate,
    DocketResponse,
    DocumentResponse,
    SecondarySourceResponse,
    AnalyticsSummary,
    ChatMessage,
} from '@/types';

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        headers: { 'Content-Type': 'application/json', ...options?.headers },
        ...options,
    });
    if (!res.ok) {
        throw new Error(`API Error: ${res.status} ${res.statusText}`);
    }
    return res.json();
}

// ─── Cases ─────────────────────────────────────────
export const casesApi = {
    list: (params?: { skip?: number; limit?: number; status?: string; jurisdiction_type?: string; area_of_application?: string; q?: string }) => {
        const query = new URLSearchParams();
        if (params?.skip) query.set('skip', String(params.skip));
        if (params?.limit) query.set('limit', String(params.limit));
        if (params?.status) query.set('status', params.status);
        if (params?.jurisdiction_type) query.set('jurisdiction_type', params.jurisdiction_type);
        if (params?.area_of_application) query.set('area_of_application', params.area_of_application);
        if (params?.q) query.set('q', params.q);
        return fetchApi<PaginatedResponse<CaseResponse>>(`/cases?${query}`);
    },
    get: (id: number) => fetchApi<CaseResponse>(`/cases/${id}`),
    create: (data: CaseCreate) => fetchApi<CaseResponse>('/cases', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: Partial<CaseCreate>) => fetchApi<CaseResponse>(`/cases/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => fetchApi<void>(`/cases/${id}`, { method: 'DELETE' }),
};

// ─── Dockets ───────────────────────────────────────
export const docketsApi = {
    list: (params?: { skip?: number; limit?: number; case_id?: number }) => {
        const query = new URLSearchParams();
        if (params?.skip) query.set('skip', String(params.skip));
        if (params?.limit) query.set('limit', String(params.limit));
        if (params?.case_id) query.set('case_id', String(params.case_id));
        return fetchApi<PaginatedResponse<DocketResponse>>(`/dockets?${query}`);
    },
    get: (id: number) => fetchApi<DocketResponse>(`/dockets/${id}`),
    create: (data: any) => fetchApi<DocketResponse>('/dockets', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: any) => fetchApi<DocketResponse>(`/dockets/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => fetchApi<void>(`/dockets/${id}`, { method: 'DELETE' }),
};

// ─── Documents ─────────────────────────────────────
export const documentsApi = {
    list: (params?: { skip?: number; limit?: number; case_id?: number }) => {
        const query = new URLSearchParams();
        if (params?.skip) query.set('skip', String(params.skip));
        if (params?.limit) query.set('limit', String(params.limit));
        if (params?.case_id) query.set('case_id', String(params.case_id));
        return fetchApi<PaginatedResponse<DocumentResponse>>(`/documents?${query}`);
    },
    get: (id: number) => fetchApi<DocumentResponse>(`/documents/${id}`),
    create: (data: any) => fetchApi<DocumentResponse>('/documents', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: any) => fetchApi<DocumentResponse>(`/documents/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => fetchApi<void>(`/documents/${id}`, { method: 'DELETE' }),
};

// ─── Secondary Sources ─────────────────────────────
export const secondarySourcesApi = {
    list: (params?: { skip?: number; limit?: number; case_id?: number }) => {
        const query = new URLSearchParams();
        if (params?.skip) query.set('skip', String(params.skip));
        if (params?.limit) query.set('limit', String(params.limit));
        if (params?.case_id) query.set('case_id', String(params.case_id));
        return fetchApi<PaginatedResponse<SecondarySourceResponse>>(`/secondary-sources?${query}`);
    },
};

// ─── Search ────────────────────────────────────────
export const searchApi = {
    search: (q: string, params?: { limit?: number; skip?: number }) => {
        const query = new URLSearchParams({ q });
        if (params?.limit) query.set('limit', String(params.limit));
        if (params?.skip) query.set('skip', String(params.skip));
        return fetchApi<PaginatedResponse<CaseResponse>>(`/search?${query}`);
    },
};

// ─── Analytics ─────────────────────────────────────
export const analyticsApi = {
    summary: () => fetchApi<AnalyticsSummary>('/analytics/summary'),
};

// ─── AI ────────────────────────────────────────────
export const aiApi = {
    chat: (messages: ChatMessage[]) => fetchApi<any>('/ai/chat', {
        method: 'POST',
        body: JSON.stringify({ messages }),
    }),
    summarize: (caseId: number) => fetchApi<any>(`/ai/summarize/${caseId}`, { method: 'POST' }),
};

// ─── Health ────────────────────────────────────────
export const healthApi = {
    check: () => fetchApi<any>('/health'),
};
