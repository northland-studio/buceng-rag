import { useState, useEffect } from 'react';
import Analyzer from './components/Analyzer';
import KnowledgeBase from './components/KnowledgeBase';
import Settings from './components/Settings';
import { analyzeApi } from './services/api';
import {
  Sparkles,
  Database,
  Activity,
  Menu,
  X,
  ExternalLink,
  Settings as SettingsIcon
} from 'lucide-react';

type Tab = 'analyzer' | 'knowledge' | 'settings';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('analyzer');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [health, setHealth] = useState<{
    status: string;
    kb_initialized: boolean;
  } | null>(null);
  const [stats, setStats] = useState<{
    total_cards: number;
    categories: Record<string, number>;
  } | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const result = await analyzeApi.healthCheck();
        setHealth(result);
      } catch (err) {
        console.error('Health check failed:', err);
      }
    };

    const fetchStats = async () => {
      try {
        const result = await analyzeApi.getStats();
        setStats(result);
      } catch (err) {
        console.error('Stats fetch failed:', err);
      }
    };

    checkHealth();
    fetchStats();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-deep)' }}>
      <header className="fixed top-0 left-0 right-0 z-40 glass-panel border-b border-[var(--border-subtle)]" style={{ borderRadius: 0 }}>
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl overflow-hidden flex items-center justify-center relative" style={{ background: 'linear-gradient(135deg, var(--accent-amber) 0%, #b45309 100%)' }}>
                <img src="/logo.png" alt="不曾社科" className="w-full h-full object-cover" />
              </div>
              <div>
                <h1 className="text-lg font-bold gradient-text" style={{ fontFamily: "'Noto Serif SC', serif" }}>不曾社科</h1>
                <p className="text-xs text-[var(--text-muted)]">RAG Analysis System</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {health && (
              <div className="hidden sm:flex items-center gap-2 text-sm px-3 py-1.5 rounded-full" style={{ background: 'var(--bg-tertiary)' }}>
                <Activity className={`w-4 h-4 ${health.status === 'healthy' ? 'text-green-400' : 'text-red-400'}`} />
                <span className="text-[var(--text-secondary)]">
                  {health.status === 'healthy' ? '系统正常' : '系统异常'}
                </span>
              </div>
            )}
            <a
              href="https://beiyu.xuanjian.top/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-sm text-[var(--text-secondary)] hover:text-[var(--accent-amber-light)] transition-colors"
            >
              北域工作室
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </header>

      <aside
        className={`fixed left-0 bottom-0 w-64 border-r border-[var(--border-subtle)] transform transition-transform z-30 lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
        style={{ background: 'var(--bg-primary)', top: '76px' }}
      >
        <div className="p-4">
          <div className="decorative-line mb-6" />
          
          <nav className="space-y-1">
            <button
              onClick={() => {
                setActiveTab('analyzer');
                setSidebarOpen(false);
              }}
              className={`nav-item w-full ${activeTab === 'analyzer' ? 'active' : ''}`}
            >
              <Sparkles className="w-5 h-5" />
              <span>事件分析</span>
            </button>
            <button
              onClick={() => {
                setActiveTab('knowledge');
                setSidebarOpen(false);
              }}
              className={`nav-item w-full ${activeTab === 'knowledge' ? 'active' : ''}`}
            >
              <Database className="w-5 h-5" />
              <span>知识库管理</span>
            </button>
            <button
              onClick={() => {
                setActiveTab('settings');
                setSidebarOpen(false);
              }}
              className={`nav-item w-full ${activeTab === 'settings' ? 'active' : ''}`}
            >
              <SettingsIcon className="w-5 h-5" />
              <span>系统设置</span>
            </button>
          </nav>

          <div className="decorative-line my-6" />

          {stats && (
            <div className="space-y-3">
              <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">知识库统计</h3>
              <div className="stat-card">
                <div className="flex items-center justify-between">
                  <span className="text-[var(--text-secondary)] text-sm">理论卡片</span>
                  <span className="text-xl font-bold gradient-text">{stats.total_cards}</span>
                </div>
              </div>
              <div className="stat-card">
                <div className="flex items-center justify-between">
                  <span className="text-[var(--text-secondary)] text-sm">分类数量</span>
                  <span className="text-xl font-bold gradient-text-teal">{Object.keys(stats.categories).length}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </aside>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-20 lg:hidden backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="lg:ml-64 p-4 md:p-6 min-h-screen" style={{ paddingTop: '100px' }}>
        <div className="max-w-5xl mx-auto">
          {activeTab === 'analyzer' && <Analyzer />}
          {activeTab === 'knowledge' && <KnowledgeBase />}
          {activeTab === 'settings' && <Settings />}
        </div>
      </main>

      <footer className="lg:ml-64 py-8 text-center border-t border-[var(--border-subtle)]" style={{ background: 'var(--bg-primary)' }}>
        <div className="decorative-line max-w-xs mx-auto mb-4" />
        <p className="text-sm text-[var(--text-muted)]">
          <span className="gradient-text font-semibold">BucengRAG</span>
          <span className="mx-2">·</span>
          不曾社科理论分析系统
        </p>
        <p className="text-xs text-[var(--text-muted)] mt-1">
          开发者：
          <a
            href="https://beiyu.xuanjian.top/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--accent-amber-light)] hover:text-[var(--accent-amber)] ml-1 transition-colors"
          >
            北域工作室
          </a>
        </p>
      </footer>
    </div>
  );
}
