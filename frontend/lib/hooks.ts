import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { casesApi, docketsApi, documentsApi, secondarySourcesApi, searchApi, analyticsApi, healthApi, aiApi } from './api';
import type { PaginatedResponse, CaseResponse, DocketResponse, DocumentResponse, SecondarySourceResponse, AnalyticsSummary } from '@/types';

// ─── Keys ──────────────────────────────────────────
export const queryKeys = {
    cases: ['cases'] as const,
    caseDetail: (id: number) => ['cases', id] as const,
    dockets: ['dockets'] as const,
    documents: ['documents'] as const,
    secondarySources: ['secondarySources'] as const,
    search: (q: string) => ['search', q] as const,
    analytics: ['analytics'] as const,
    health: ['health'] as const,
};

// ─── Case Hooks ────────────────────────────────────
export function useCases(params?: { skip?: number; limit?: number; status?: string; jurisdiction_type?: string; area_of_application?: string; q?: string }) {
    return useQuery<PaginatedResponse<CaseResponse>>({
        queryKey: [...queryKeys.cases, params],
        queryFn: () => casesApi.list(params),
        placeholderData: (prev: any) => prev,
    });
}

export function useCase(id: number) {
    return useQuery<CaseResponse>({
        queryKey: queryKeys.caseDetail(id),
        queryFn: () => casesApi.get(id),
        enabled: !!id,
    });
}

export function useCreateCase() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: casesApi.create,
        onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.cases }),
    });
}

export function useDeleteCase() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: casesApi.delete,
        onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.cases }),
    });
}

// ─── Docket Hooks ──────────────────────────────────
export function useDockets(params?: { skip?: number; limit?: number; case_id?: number }) {
    return useQuery<PaginatedResponse<DocketResponse>>({
        queryKey: [...queryKeys.dockets, params],
        queryFn: () => docketsApi.list(params),
        placeholderData: (prev: any) => prev,
    });
}

// ─── Document Hooks ────────────────────────────────
export function useDocuments(params?: { skip?: number; limit?: number; case_id?: number }) {
    return useQuery<PaginatedResponse<DocumentResponse>>({
        queryKey: [...queryKeys.documents, params],
        queryFn: () => documentsApi.list(params),
        placeholderData: (prev: any) => prev,
    });
}

// ─── Secondary Source Hooks ────────────────────────
export function useSecondarySources(params?: { skip?: number; limit?: number; case_id?: number }) {
    return useQuery<PaginatedResponse<SecondarySourceResponse>>({
        queryKey: [...queryKeys.secondarySources, params],
        queryFn: () => secondarySourcesApi.list(params),
        placeholderData: (prev: any) => prev,
    });
}

// ─── Search Hook ───────────────────────────────────
export function useSearch(q: string) {
    return useQuery<PaginatedResponse<CaseResponse>>({
        queryKey: queryKeys.search(q),
        queryFn: () => searchApi.search(q),
        enabled: q.length >= 2,
    });
}

// ─── Analytics Hook ────────────────────────────────
export function useAnalytics() {
    return useQuery<AnalyticsSummary>({
        queryKey: queryKeys.analytics,
        queryFn: analyticsApi.summary,
    });
}

// ─── Health Hook ───────────────────────────────────
export function useHealth() {
    return useQuery({
        queryKey: queryKeys.health,
        queryFn: healthApi.check,
        refetchInterval: 30_000,
    });
}
