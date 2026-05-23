import { useState, useEffect } from 'react';
import { analyzeApi } from '../services/api';
import type { StatsResponse } from '../types';
import {
  Settings as SettingsIcon,
  Cpu,
  Database,
  Brain,
  Server,
  Info,
  ExternalLink,
  Activity
} from 'lucide-react';

export default function Settings() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [health, setHealth] = useState<{
    status: string;
    kb_initialized: boolean;
    llm_initialized: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, healthData] = await Promise.all([
          analyzeApi.getStats(),
          analyzeApi.healthCheck(),
        ]);
        setStats(statsData);
        setHealth(healthData);
      } catch (err) {
        console.error('Failed to fetch data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3" style={{ fontFamily: "'Noto Serif SC', serif" }}>
              <SettingsIcon className="w-6 h-6 text-[var(--accent-amber-light)]" />
              <span className="gradient-text">系统设置</span>
            </h2>
            <p className="text-sm text-[var(--text-muted)] mt-1">
              查看系统信息和配置
            </p>
          </div>
        </div>

        <div className="decorative-line mb-6" />

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton h-20 rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="glass-panel p-5" style={{ background: 'var(--bg-secondary)' }}>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                <Activity className="w-5 h-5 text-[var(--accent-teal-light)]" />
                系统状态
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-xl" style={{ background: 'var(--bg-tertiary)' }}>
                  <div className={`w-3 h-3 rounded-full ${health?.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'}`} />
                  <div>
                    <p className="text-sm text-[var(--text-secondary)]">API 状态</p>
                    <p className="font-medium text-[var(--text-primary)]">
                      {health?.status === 'healthy' ? '正常运行' : '异常'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-xl" style={{ background: 'var(--bg-tertiary)' }}>
                  <div className={`w-3 h-3 rounded-full ${health?.kb_initialized ? 'bg-green-400' : 'bg-yellow-400'}`} />
                  <div>
                    <p className="text-sm text-[var(--text-secondary)]">知识库</p>
                    <p className="font-medium text-[var(--text-primary)]">
                      {health?.kb_initialized ? '已初始化' : '未初始化'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-xl" style={{ background: 'var(--bg-tertiary)' }}>
                  <div className={`w-3 h-3 rounded-full ${health?.llm_initialized ? 'bg-green-400' : 'bg-yellow-400'}`} />
                  <div>
                    <p className="text-sm text-[var(--text-secondary)]">LLM 服务</p>
                    <p className="font-medium text-[var(--text-primary)]">
                      {health?.llm_initialized ? '已初始化' : '未初始化'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="glass-panel p-5" style={{ background: 'var(--bg-secondary)' }}>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                <Database className="w-5 h-5 text-[var(--accent-amber-light)]" />
                知识库信息
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="stat-card">
                  <p className="text-2xl font-bold gradient-text">{stats?.total_cards || 0}</p>
                  <p className="text-sm text-[var(--text-secondary)]">总卡片数</p>
                </div>
                <div className="stat-card">
                  <p className="text-2xl font-bold gradient-text-teal">{Object.keys(stats?.categories || {}).length}</p>
                  <p className="text-sm text-[var(--text-secondary)]">分类数量</p>
                </div>
                <div className="stat-card col-span-2">
                  <p className="text-sm text-[var(--text-secondary)] mb-2">嵌入模型</p>
                  <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                    {stats?.embedding_model || 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            <div className="glass-panel p-5" style={{ background: 'var(--bg-secondary)' }}>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                <Brain className="w-5 h-5 text-[var(--accent-amber-light)]" />
                模型配置
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 rounded-xl" style={{ background: 'var(--bg-tertiary)' }}>
                  <div className="flex items-center gap-3">
                    <Cpu className="w-5 h-5 text-[var(--text-muted)]" />
                    <span className="text-[var(--text-secondary)]">LLM 模型</span>
                  </div>
                  <span className="tag tag-accent">{stats?.llm_model || 'N/A'}</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl" style={{ background: 'var(--bg-tertiary)' }}>
                  <div className="flex items-center gap-3">
                    <Server className="w-5 h-5 text-[var(--text-muted)]" />
                    <span className="text-[var(--text-secondary)]">嵌入模型</span>
                  </div>
                  <span className="tag">{stats?.embedding_model || 'N/A'}</span>
                </div>
              </div>
            </div>

            <div className="glass-panel p-5" style={{ background: 'var(--bg-secondary)' }}>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                <Info className="w-5 h-5 text-[var(--accent-teal-light)]" />
                关于系统
              </h3>
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, var(--accent-amber) 0%, #b45309 100%)' }}>
                    <Database className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-[var(--text-primary)]" style={{ fontFamily: "'Noto Serif SC', serif" }}>BucengRAG</h4>
                    <p className="text-sm text-[var(--text-secondary)] mt-1">
                      不曾社科理论分析系统 - 基于 RAG 架构的社会科学分析工具
                    </p>
                    <p className="text-xs text-[var(--text-muted)] mt-2">版本 1.0.0</p>
                  </div>
                </div>
                <div className="decorative-line" />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[var(--text-secondary)]">开发者</span>
                  <a
                    href="https://beiyu.xuanjian.top/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-sm text-[var(--accent-amber-light)] hover:text-[var(--accent-amber)] transition-colors"
                  >
                    北域工作室
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
