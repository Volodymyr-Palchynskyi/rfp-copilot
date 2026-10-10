export type Budget = 'budget' | 'standard' | 'enterprise';

export interface ProposalRequest {
  client_name: string;
  project_description: string;
  budget_level: Budget;
  target_timeline_weeks: number | null;
}

export interface TechStackItem {
  category: string;
  name: string;
  reason: string;
}

export interface FeatureEstimate {
  module: string;
  title: string;
  description: string;
  complexity: 'low' | 'medium' | 'high';
  hours_min: number;
  hours_max: number;
}

export interface RiskItem {
  risk: string;
  impact: 'low' | 'medium' | 'high';
  mitigation: string;
}

export interface ReferenceProject {
  project_id: string;
  title: string;
  industry: string;
  stack: string;
  total_hours: number;
  duration_weeks: number;
  relevance_score: number;
  matched_sections: string[];
  reason?: string | null;
}

export interface ProposalDraft {
  project_title: string;
  executive_summary: string;
  architecture_overview: string;
  tech_stack: TechStackItem[];
  features: FeatureEstimate[];
  risks: RiskItem[];
  estimated_duration_weeks: number;
  estimation_basis: string;
}

export interface Usage {
  model: string;
  input_tokens: number;
  output_tokens: number;
  thinking_tokens: number;
  total_tokens: number;
  latency_s: number;
  first_token_s: number | null;
  estimated_cost_usd: number | null;
}

export interface ProposalResponse extends ProposalDraft {
  total_hours_min: number;
  total_hours_max: number;
  references: ReferenceProject[];
  usage: Usage | null;
}

/**
 * While streaming, any field can be missing and the last list item can be half written,
 * so the UI works with this deeply partial view of the draft.
 */
export interface PartialDraft {
  project_title?: string;
  executive_summary?: string;
  architecture_overview?: string;
  tech_stack?: Partial<TechStackItem>[];
  features?: Partial<FeatureEstimate>[];
  risks?: Partial<RiskItem>[];
  estimated_duration_weeks?: number;
  estimation_basis?: string;
}

export type StreamEvent =
  | { event: 'references'; data: ReferenceProject[] }
  | { event: 'section'; data: { key: keyof PartialDraft; value: unknown } }
  | { event: 'notice'; data: { fallback_model: string } }
  | { event: 'complete'; data: ProposalResponse }
  | { event: 'error'; data: { detail: string } };
