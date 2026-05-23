import axios from 'axios';
import type { AnalyzeRequest, AnalyzeResponse, StatsResponse, Card } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface StreamMessage {
  type: 'cards' | 'history' | 'chunk' | 'done' | 'error';
  data?: any;
  message?: string;
  model?: string;
}

export interface ExportRequest {
  event_text: string;
  analysis: string;
  retrieved_cards: any[];
  llm_model: string;
}

export const analyzeApi = {
  analyze: async (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const response = await api.post<AnalyzeResponse>('/api/analyze', request);
    return response.data;
  },

  analyzeStream: async (
    request: AnalyzeRequest,
    onMessage: (message: StreamMessage) => void,
    onError: (error: string) => void
  ): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE}/api/analyze/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        onError(errorData.detail || '请求失败');
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        onError('无法读取响应流');
        return;
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6);
              const message: StreamMessage = JSON.parse(jsonStr);
              onMessage(message);
            } catch (e) {
              console.error('解析消息失败:', e);
            }
          }
        }
      }
    } catch (error: any) {
      onError(error.message || '网络错误');
    }
  },

  search: async (query: string, k: number = 5): Promise<{ results: Card[]; count: number }> => {
    const response = await api.post('/api/search', { query, k });
    return response.data;
  },

  getStats: async (): Promise<StatsResponse> => {
    const response = await api.get<StatsResponse>('/api/stats');
    return response.data;
  },

  getCards: async (category?: string, limit: number = 100): Promise<{ cards: Card[]; count: number }> => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    params.append('limit', limit.toString());
    const response = await api.get(`/api/cards?${params.toString()}`);
    return response.data;
  },

  addCard: async (card: Omit<Card, 'id' | 'created_at'>): Promise<{ message: string; card: Card }> => {
    const response = await api.post('/api/cards', card);
    return response.data;
  },

  deleteCard: async (cardId: string): Promise<{ message: string }> => {
    const response = await api.delete(`/api/cards/${cardId}`);
    return response.data;
  },

  uploadDocument: async (file: File): Promise<{ message: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  exportMarkdown: async (request: ExportRequest): Promise<Blob> => {
    const response = await api.post('/api/export/markdown', request, {
      responseType: 'blob',
    });
    return response.data;
  },

  exportDocx: async (request: ExportRequest): Promise<Blob> => {
    const response = await api.post('/api/export/docx', request, {
      responseType: 'blob',
    });
    return response.data;
  },

  healthCheck: async (): Promise<{ status: string; kb_initialized: boolean; llm_initialized: boolean }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
