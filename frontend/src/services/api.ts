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

export const analyzeApi = {
  analyze: async (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const response = await api.post<AnalyzeResponse>('/api/analyze', request);
    return response.data;
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

  exportMarkdown: async (request: AnalyzeRequest): Promise<Blob> => {
    const response = await api.post('/api/export/markdown', request, {
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
