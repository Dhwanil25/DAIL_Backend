export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    skip: number;
    limit: number;
}

export interface CaseResponse {
    id: number;
    record_number: number;
    case_slug: string | null;
    caption: string;
    brief_description: string | null;
    area_of_application: string | null;
    area_of_application_text: string | null;
    issue_text: string | null;
    issue_list: string | null;
    cause_of_action_list: string | null;
    cause_of_action_text: string | null;
    name_of_algorithm_list: string | null;
    name_of_algorithm_text: string | null;
    class_action_list: string | null;
    class_action: string | null;
    organizations_involved: string | null;
    jurisdiction_filed: string | null;
    date_action_filed: string | null;
    current_jurisdiction: string | null;
    jurisdiction_type: string | null;
    jurisdiction_type_text: string | null;
    jurisdiction_name: string | null;
    published_opinions: string | null;
    published_opinions_binary: boolean;
    status_disposition: string | null;
    progress_notes: string | null;
    researcher: string | null;
    summary_of_significance: string | null;
    summary_facts_activity: string | null;
    most_recent_activity: string | null;
    most_recent_activity_date: string | null;
    keyword: string | null;
    date_added: string | null;
    last_update: string | null;
}

export interface CaseCreate {
    record_number: number;
    caption: string;
    case_slug?: string | null;
    brief_description?: string | null;
    area_of_application?: string | null;
    area_of_application_text?: string | null;
    issue_text?: string | null;
    issue_list?: string | null;
    cause_of_action_list?: string | null;
    cause_of_action_text?: string | null;
    name_of_algorithm_list?: string | null;
    name_of_algorithm_text?: string | null;
    class_action_list?: string | null;
    class_action?: string | null;
    organizations_involved?: string | null;
    jurisdiction_filed?: string | null;
    date_action_filed?: string | null;
    current_jurisdiction?: string | null;
    jurisdiction_type?: string | null;
    jurisdiction_type_text?: string | null;
    jurisdiction_name?: string | null;
    published_opinions?: string | null;
    published_opinions_binary?: boolean;
    status_disposition?: string | null;
    progress_notes?: string | null;
    researcher?: string | null;
    summary_of_significance?: string | null;
    summary_facts_activity?: string | null;
    most_recent_activity?: string | null;
    most_recent_activity_date?: string | null;
    keyword?: string | null;
}

export interface DocketResponse {
    id: number;
    case_number: number;
    court: string | null;
    number: string | null;
    link: string | null;
}

export interface DocumentResponse {
    id: number;
    case_number: number;
    court: string | null;
    date: string | null;
    link: string | null;
    cite_or_reference: string | null;
    document: string | null;
}

export interface SecondarySourceResponse {
    id: number;
    case_number: number;
    secondary_source_link: string | null;
    secondary_source_title: string | null;
}

export interface AnalyticsSummary {
    totals: {
        cases: number;
        dockets: number;
        documents: number;
        secondary_sources: number;
    };
    status_breakdown: { status: string; count: number }[];
    jurisdiction_type_breakdown: { jurisdiction_type: string; count: number }[];
    area_breakdown: { area: string; count: number }[];
    yearly_filings: { year: number; count: number }[];
}

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
}
