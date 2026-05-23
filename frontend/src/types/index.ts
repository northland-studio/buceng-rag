export interface Card {
  id: string;
  title: string;
  content: string;
  category: string;
  keywords: string[];
  source: string;
  created_at?: string;
}

export interface HistoryRecord {
  id: string;
  title: string;
  content: string;
  period: string;
  source: string;
  keywords: string[];
}

export interface AnalyzeRequest {
  event_text: string;
  analysis_mode: 'minecraft' | 'general';
  temperature?: number;
  thinking_enabled: boolean;
  reasoning_effort: 'low' | 'medium' | 'high';
  max_results: number;
  api_key?: string;
  base_url?: string;
}

export interface AnalyzeResponse {
  analysis: string;
  retrieved_cards: Card[];
  history_records: HistoryRecord[];
  model: string;
}

export interface StatsResponse {
  total_cards: number;
  categories: Record<string, number>;
  embedding_model: string;
  llm_model: string;
}
