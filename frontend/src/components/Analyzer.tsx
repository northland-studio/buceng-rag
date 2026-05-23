import { useState, useEffect } from 'react';
import { analyzeApi, type StreamMessage } from '../services/api';
import type { AnalyzeResponse, Card, HistoryRecord } from '../types';
import ReactMarkdown from 'react-markdown';
import {
  Send,
  Loader2,
  Download,
  BookOpen,
  History,
  Settings,
  ChevronDown,
  Sparkles,
  FileText,
  Copy,
  Check,
  Star,
  Key,
  Eye,
  EyeOff,
  FileDown,
  Zap
} from 'lucide-react';

type AnalysisMode = 'minecraft' | 'general';
type ReasoningEffort = 'low' | 'medium' | 'high';

const STORAGE_KEYS = {
  API_KEY: 'buceng_api_key',
  BASE_URL: 'buceng_base_url',
};

export default function Analyzer() {
  const [eventText, setEventText] = useState('');
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>('minecraft');
  const [thinkingEnabled, setThinkingEnabled] = useState(true);
  const [reasoningEffort, setReasoningEffort] = useState<ReasoningEffort>('high');
  const [maxResults, setMaxResults] = useState(5);
  const [temperature, setTemperature] = useState(0.3);
  const [streamingEnabled, setStreamingEnabled] = useState(true);
  
  const [apiKey, setApiKey] = useState(() => localStorage.getItem(STORAGE_KEYS.API_KEY) || '');
  const [baseUrl, setBaseUrl] = useState(() => localStorage.getItem(STORAGE_KEYS.BASE_URL) || '');
  const [showApiKey, setShowApiKey] = useState(false);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [streamingText, setStreamingText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(true);
  const [copied, setCopied] = useState(false);
  const [rating, setRating] = useState<number | null>(null);

  useEffect(() => {
    if (apiKey) {
      localStorage.setItem(STORAGE_KEYS.API_KEY, apiKey);
    } else {
      localStorage.removeItem(STORAGE_KEYS.API_KEY);
    }
  }, [apiKey]);

  useEffect(() => {
    if (baseUrl) {
      localStorage.setItem(STORAGE_KEYS.BASE_URL, baseUrl);
    } else {
      localStorage.removeItem(STORAGE_KEYS.BASE_URL);
    }
  }, [baseUrl]);

  const buildRequest = () => ({
    event_text: eventText,
    analysis_mode: analysisMode,
    temperature,
    thinking_enabled: thinkingEnabled,
    reasoning_effort: reasoningEffort,
    max_results: maxResults,
    api_key: apiKey,
    base_url: baseUrl || undefined,
  });

  const handleAnalyze = async () => {
    if (!eventText.trim()) {
      setError('请输入事件描述');
      return;
    }

    if (!apiKey.trim()) {
      setError('请输入 API Key');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setStreamingText('');
    setRating(null);

    if (streamingEnabled) {
      await handleStreamAnalyze();
    } else {
      await handleNormalAnalyze();
    }
  };

  const handleStreamAnalyze = async () => {
    const tempResult: Partial<AnalyzeResponse> = {
      analysis: '',
      retrieved_cards: [],
      history_records: [],
      model: ''
    };

    await analyzeApi.analyzeStream(
      buildRequest(),
      (message: StreamMessage) => {
        switch (message.type) {
          case 'cards':
            tempResult.retrieved_cards = message.data || [];
            break;
          case 'history':
            tempResult.history_records = message.data || [];
            break;
          case 'chunk':
            tempResult.analysis = (tempResult.analysis || '') + (message.data || '');
            setStreamingText(tempResult.analysis);
            break;
          case 'done':
            tempResult.model = message.model || '';
            setResult(tempResult as AnalyzeResponse);
            setLoading(false);
            break;
          case 'error':
            setError(message.message || '分析失败');
            setLoading(false);
            break;
        }
      },
      (errorMsg: string) => {
        setError(errorMsg);
        setLoading(false);
      }
    );
  };

  const handleNormalAnalyze = async () => {
    try {
      const response = await analyzeApi.analyze(buildRequest());
      setResult(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || '分析失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleExportMarkdown = async () => {
    if (!result) return;

    try {
      const blob = await analyzeApi.exportMarkdown({
        event_text: eventText,
        analysis: result.analysis,
        retrieved_cards: result.retrieved_cards,
        llm_model: result.model || 'DeepSeek'
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_${new Date().toISOString().slice(0, 10)}.md`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const handleExportDocx = async () => {
    if (!result) return;

    try {
      const blob = await analyzeApi.exportDocx({
        event_text: eventText,
        analysis: result.analysis,
        retrieved_cards: result.retrieved_cards,
        llm_model: result.model || 'DeepSeek'
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_${new Date().toISOString().slice(0, 10)}.docx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export DOCX failed:', err);
    }
  };

  const handleCopy = async () => {
    if (!result) return;
    await navigator.clipboard.writeText(result.analysis);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const displayAnalysis = streamingEnabled && loading ? streamingText : result?.analysis;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="glass-panel-accent p-6 relative overflow-hidden">
        <div className="decorative-corner top-left" />
        <div className="decorative-corner bottom-right" />

        <div className="flex items-center justify-between mb-6 relative z-10">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3" style={{ fontFamily: "'Noto Serif SC', serif" }}>
              <Sparkles className="w-6 h-6 text-[var(--accent-amber-light)]" />
              <span className="gradient-text">事件分析</span>
            </h2>
            <p className="text-sm text-[var(--text-muted)] mt-1">
              基于RAG架构的社会科学理论分析
            </p>
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center gap-2 text-sm text-[var(--text-secondary)] hover:text-[var(--accent-amber-light)] transition-colors px-3 py-2 rounded-lg hover:bg-[var(--bg-tertiary)]"
          >
            <Settings className="w-4 h-4" />
            高级设置
            <ChevronDown className={`w-4 h-4 transition-transform ${showSettings ? 'rotate-180' : ''}`} />
          </button>
        </div>

        <div className="space-y-5 relative z-10">
          <div className="mode-toggle">
            <button
              onClick={() => setAnalysisMode('minecraft')}
              className={analysisMode === 'minecraft' ? 'active' : ''}
            >
              Minecraft 游戏分析
            </button>
            <button
              onClick={() => setAnalysisMode('general')}
              className={analysisMode === 'general' ? 'active' : ''}
            >
              普通社科分析
            </button>
          </div>

          <div className="relative">
            <textarea
              value={eventText}
              onChange={(e) => setEventText(e.target.value)}
              placeholder={
                analysisMode === 'minecraft'
                  ? '描述 Minecraft 游戏内的社会现象或事件，例如：玩家在公共农场收割后不补种，导致冲突并催生规则...'
                  : '描述现实社会现象或事件，例如：某企业实行996工作制，员工普遍感到压力过大，出现离职潮...'
              }
              className="input-field w-full h-44 resize-none text-base leading-relaxed"
              style={{ fontFamily: "'Noto Serif SC', serif" }}
            />
            <div className="absolute bottom-3 right-3 text-xs text-[var(--text-muted)]">
              {eventText.length} 字符
            </div>
          </div>

          {showSettings && (
            <div className="space-y-4 p-5 rounded-xl animate-slide-up" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)' }}>
              <div className="flex items-center gap-2 text-sm font-medium text-[var(--accent-amber-light)]">
                <Key className="w-4 h-4" />
                API 配置（必填）
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">
                    API Key <span className="text-red-400">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showApiKey ? 'text' : 'password'}
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="sk-..."
                      className="input-field pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                    >
                      {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">API 地址</label>
                  <input
                    type="text"
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                    placeholder="https://api.deepseek.com"
                    className="input-field"
                  />
                </div>
              </div>
              
              <div className="decorative-line my-4" />
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">检索数量</label>
                  <input
                    type="number"
                    value={maxResults}
                    onChange={(e) => setMaxResults(Number(e.target.value))}
                    min={1}
                    max={20}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">温度参数</label>
                  <input
                    type="number"
                    value={temperature}
                    onChange={(e) => setTemperature(Number(e.target.value))}
                    min={0}
                    max={2}
                    step={0.1}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">推理强度</label>
                  <select
                    value={reasoningEffort}
                    onChange={(e) => setReasoningEffort(e.target.value as ReasoningEffort)}
                    className="input-field"
                  >
                    <option value="low">快速</option>
                    <option value="medium">中等</option>
                    <option value="high">深度</option>
                  </select>
                </div>
                <div className="flex flex-col justify-end gap-2">
                  <label className="flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={streamingEnabled}
                      onChange={(e) => setStreamingEnabled(e.target.checked)}
                      className="w-4 h-4 rounded accent-[var(--accent-amber)]"
                    />
                    <Zap className="w-4 h-4 text-[var(--accent-teal-light)]" />
                    <span className="text-sm text-[var(--text-secondary)]">流式</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={thinkingEnabled}
                      onChange={(e) => setThinkingEnabled(e.target.checked)}
                      className="w-4 h-4 rounded accent-[var(--accent-amber)]"
                    />
                    <span className="text-sm text-[var(--text-secondary)]">思考</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={handleAnalyze}
              disabled={loading || !eventText.trim()}
              className="btn-primary flex-1 text-base py-3.5"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {streamingEnabled ? '分析中...' : '分析中...'}
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  开始分析
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl animate-slide-up" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {(displayAnalysis || result) && (
        <div className="space-y-6 animate-slide-up">
          <div className="glass-panel p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                <FileText className="w-5 h-5 text-[var(--accent-amber-light)]" />
                分析结果
                {result?.model && (
                  <span className="tag tag-accent ml-2">
                    {result.model}
                  </span>
                )}
                {loading && streamingEnabled && (
                  <span className="tag tag-teal ml-2 animate-pulse">实时生成中</span>
                )}
              </h3>
              <div className="flex items-center gap-2">
                {result && (
                  <>
                    <button
                      onClick={handleCopy}
                      className="flex items-center gap-1 text-sm text-[var(--text-secondary)] hover:text-[var(--accent-amber-light)] transition-colors"
                    >
                      {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                      {copied ? '已复制' : '复制'}
                    </button>
                    <button
                      onClick={handleExportMarkdown}
                      className="flex items-center gap-1 text-sm text-[var(--text-secondary)] hover:text-[var(--accent-amber-light)] transition-colors px-2 py-1 rounded-lg hover:bg-[var(--bg-tertiary)]"
                    >
                      <Download className="w-4 h-4" />
                      MD
                    </button>
                    <button
                      onClick={handleExportDocx}
                      className="flex items-center gap-1 text-sm text-[var(--text-secondary)] hover:text-[var(--accent-amber-light)] transition-colors px-2 py-1 rounded-lg hover:bg-[var(--bg-tertiary)]"
                    >
                      <FileDown className="w-4 h-4" />
                      Word
                    </button>
                  </>
                )}
              </div>
            </div>
            <div className="markdown-content prose prose-invert max-w-none">
              <ReactMarkdown>{displayAnalysis || ''}</ReactMarkdown>
            </div>
          </div>

          {result?.retrieved_cards && result.retrieved_cards.length > 0 && (
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                <BookOpen className="w-5 h-5 text-[var(--accent-amber-light)]" />
                引用的理论卡片
                <span className="tag ml-2">{result.retrieved_cards.length}</span>
              </h3>
              <div className="space-y-3">
                {result.retrieved_cards.map((card, index) => (
                  <TheoryCard key={card.id || index} card={card} />
                ))}
              </div>
            </div>
          )}

          {result?.history_records && result.history_records.length > 0 && (
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                <History className="w-5 h-5 text-[var(--accent-teal-light)]" />
                历史参考
                <span className="tag tag-teal ml-2">{result.history_records.length}</span>
              </h3>
              <div className="space-y-3">
                {result.history_records.map((record, index) => (
                  <HistoryCard key={record.id || index} record={record} />
                ))}
              </div>
            </div>
          )}

          {result && (
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                <Star className="w-5 h-5 text-[var(--accent-amber-light)]" />
                评价分析结果
              </h3>
              <div className="flex items-center gap-4">
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((value) => (
                    <button
                      key={value}
                      onClick={() => setRating(value)}
                      className={`p-2 rounded-lg transition-all ${rating === value
                          ? 'bg-[var(--accent-amber)] text-white'
                          : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]'
                        }`}
                    >
                      <Star className={`w-5 h-5 ${rating && rating >= value ? 'fill-current' : ''}`} />
                    </button>
                  ))}
                </div>
                <span className="text-sm text-[var(--text-muted)]">
                  {rating ? `您选择了 ${rating} 星` : '点击星星评分'}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TheoryCard({ card }: { card: Card }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card-elevated p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-[var(--text-primary)]" style={{ fontFamily: "'Noto Serif SC', serif" }}>{card.title}</h4>
          <div className="flex items-center gap-2 mt-1.5">
            <span className="tag text-xs">{card.category}</span>
            {card.source && (
              <span className="text-xs text-[var(--text-muted)] truncate">{card.source}</span>
            )}
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-[var(--accent-amber-light)] hover:text-[var(--accent-amber)] whitespace-nowrap transition-colors"
        >
          {expanded ? '收起' : '展开'}
        </button>
      </div>
      {expanded && (
        <div className="mt-4 pt-4 border-t border-[var(--border-subtle)]">
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            {card.content}
          </p>
          {card.keywords && card.keywords.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {card.keywords.map((keyword, i) => (
                <span key={i} className="tag text-xs">{keyword}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function HistoryCard({ record }: { record: HistoryRecord }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card-elevated p-4" style={{ background: 'var(--bg-secondary)', opacity: 0.9 }}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-[var(--text-primary)]" style={{ fontFamily: "'Noto Serif SC', serif" }}>{record.title}</h4>
          <div className="flex items-center gap-2 mt-1.5">
            {record.period && (
              <span className="tag tag-teal text-xs">{record.period}</span>
            )}
            {record.source && (
              <span className="text-xs text-[var(--text-muted)] truncate">{record.source}</span>
            )}
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-[var(--accent-teal-light)] hover:text-[var(--accent-teal)] whitespace-nowrap transition-colors"
        >
          {expanded ? '收起' : '展开'}
        </button>
      </div>
      {expanded && (
        <div className="mt-4 pt-4 border-t border-[var(--border-subtle)]">
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            {record.content}
          </p>
        </div>
      )}
    </div>
  );
}
