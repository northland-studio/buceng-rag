import { useState, useEffect } from 'react';
import { analyzeApi } from '../services/api';
import type { Card, StatsResponse } from '../types';
import {
  Database,
  Plus,
  Trash2,
  Upload,
  Search,
  RefreshCw,
  X,
  Check,
  BookOpen,
  Tag,
  FileJson,
  AlertCircle
} from 'lucide-react';

type ViewTab = 'cards' | 'history' | 'add' | 'import';

export default function KnowledgeBase() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<ViewTab>('cards');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCard, setNewCard] = useState({
    title: '',
    content: '',
    category: 'general',
    keywords: '',
    source: '',
  });
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3000);
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsData, cardsData] = await Promise.all([
        analyzeApi.getStats(),
        analyzeApi.getCards(undefined, 100),
      ]);
      setStats(statsData);
      setCards(cardsData.cards);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      showNotification('error', '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchData();
      return;
    }
    setLoading(true);
    try {
      const result = await analyzeApi.search(searchQuery, 20);
      setCards(result.results);
    } catch (err) {
      console.error('Search failed:', err);
      showNotification('error', '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCard = async () => {
    if (!newCard.title || !newCard.content) {
      showNotification('error', '请填写标题和内容');
      return;
    }

    try {
      await analyzeApi.addCard({
        title: newCard.title,
        content: newCard.content,
        category: newCard.category,
        keywords: newCard.keywords.split(',').map(k => k.trim()).filter(Boolean),
        source: newCard.source,
      });
      setShowAddForm(false);
      setNewCard({ title: '', content: '', category: 'general', keywords: '', source: '' });
      fetchData();
      showNotification('success', '卡片添加成功');
    } catch (err) {
      console.error('Failed to add card:', err);
      showNotification('error', '添加失败');
    }
  };

  const handleDeleteCard = async (cardId: string) => {
    if (!confirm('确定要删除这张卡片吗？')) return;

    try {
      await analyzeApi.deleteCard(cardId);
      fetchData();
      showNotification('success', '卡片删除成功');
    } catch (err) {
      console.error('Failed to delete card:', err);
      showNotification('error', '删除失败');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      await analyzeApi.uploadDocument(file);
      fetchData();
      showNotification('success', '文档导入成功');
    } catch (err) {
      console.error('Upload failed:', err);
      showNotification('error', '导入失败');
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {notification && (
        <div
          className={`fixed top-20 right-4 z-50 px-4 py-3 rounded-xl animate-slide-up flex items-center gap-2 ${notification.type === 'success'
              ? 'bg-green-500/20 border border-green-500/30 text-green-400'
              : 'bg-red-500/20 border border-red-500/30 text-red-400'
            }`}
        >
          {notification.type === 'success' ? <Check className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          {notification.message}
        </div>
      )}

      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3" style={{ fontFamily: "'Noto Serif SC', serif" }}>
              <Database className="w-6 h-6 text-[var(--accent-amber-light)]" />
              <span className="gradient-text">知识库管理</span>
            </h2>
            <p className="text-sm text-[var(--text-muted)] mt-1">
              管理理论卡片和历史资料
            </p>
          </div>
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2 text-[var(--text-secondary)] hover:text-[var(--accent-amber-light)] transition-colors rounded-lg hover:bg-[var(--bg-tertiary)]"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="stat-card">
              <p className="text-3xl font-bold gradient-text">{stats.total_cards}</p>
              <p className="text-sm text-[var(--text-secondary)] mt-1">理论卡片</p>
            </div>
            <div className="stat-card">
              <p className="text-3xl font-bold gradient-text-teal">{Object.keys(stats.categories).length}</p>
              <p className="text-sm text-[var(--text-secondary)] mt-1">分类数量</p>
            </div>
            <div className="stat-card col-span-2">
              <p className="text-sm text-[var(--text-secondary)] mb-2">分类分布</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(stats.categories).slice(0, 6).map(([cat, count]) => (
                  <span key={cat} className="tag">
                    {cat}: {count}
                  </span>
                ))}
                {Object.keys(stats.categories).length > 6 && (
                  <span className="tag">+{Object.keys(stats.categories).length - 6}</span>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="decorative-line mb-6" />

        <div className="flex flex-wrap gap-3 mb-6">
          <div className="flex-1 min-w-[200px] relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--text-muted)]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="搜索知识库..."
              className="input-field pl-10"
            />
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="btn-primary"
          >
            <Plus className="w-4 h-4" />
            添加卡片
          </button>
          <label className="btn-secondary cursor-pointer">
            <Upload className="w-4 h-4" />
            导入
            <input
              type="file"
              accept=".json,.jsonl"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>

        <div className="mode-toggle mb-6">
          <button
            onClick={() => setActiveTab('cards')}
            className={activeTab === 'cards' ? 'active' : ''}
          >
            <BookOpen className="w-4 h-4 inline mr-1" />
            理论卡片
          </button>
          <button
            onClick={() => setActiveTab('import')}
            className={activeTab === 'import' ? 'active' : ''}
          >
            <FileJson className="w-4 h-4 inline mr-1" />
            批量导入
          </button>
        </div>

        {activeTab === 'cards' && (
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="skeleton h-24 rounded-xl" />
                ))}
              </div>
            ) : cards.length === 0 ? (
              <div className="text-center py-12">
                <Database className="w-12 h-12 text-[var(--text-muted)] mx-auto mb-3" />
                <p className="text-[var(--text-secondary)]">暂无数据</p>
                <p className="text-sm text-[var(--text-muted)] mt-1">点击"添加卡片"或"导入"开始</p>
              </div>
            ) : (
              cards.map((card) => (
                <CardItem key={card.id} card={card} onDelete={handleDeleteCard} />
              ))
            )}
          </div>
        )}

        {activeTab === 'import' && (
          <div className="glass-panel p-6 text-center" style={{ background: 'var(--bg-secondary)' }}>
            <FileJson className="w-16 h-16 text-[var(--accent-amber-light)] mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>批量导入</h3>
            <p className="text-[var(--text-secondary)] mb-4">
              支持 JSON 和 JSONL 格式文件
            </p>
            <label className="btn-primary cursor-pointer inline-flex">
              <Upload className="w-4 h-4" />
              选择文件
              <input
                type="file"
                accept=".json,.jsonl"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
            <div className="mt-6 p-4 rounded-xl text-left" style={{ background: 'var(--bg-tertiary)' }}>
              <p className="text-sm text-[var(--text-secondary)] mb-2">JSON 格式示例：</p>
              <pre className="text-xs text-[var(--text-muted)] overflow-x-auto">
{`[
  {
    "id": "theory_001",
    "title": "理论标题",
    "content": "理论内容...",
    "category": "分类",
    "keywords": ["关键词1", "关键词2"],
    "source": "来源"
  }
]`}
              </pre>
            </div>
          </div>
        )}
      </div>

      {showAddForm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm p-4">
          <div className="glass-panel-accent p-6 w-full max-w-lg animate-scale-in">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold gradient-text" style={{ fontFamily: "'Noto Serif SC', serif" }}>添加新卡片</h3>
              <button
                onClick={() => setShowAddForm(false)}
                className="p-1 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">标题 *</label>
                <input
                  type="text"
                  value={newCard.title}
                  onChange={(e) => setNewCard({ ...newCard, title: e.target.value })}
                  placeholder="理论卡片标题"
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">内容 *</label>
                <textarea
                  value={newCard.content}
                  onChange={(e) => setNewCard({ ...newCard, content: e.target.value })}
                  rows={4}
                  placeholder="详细描述理论内容..."
                  className="input-field resize-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">分类</label>
                  <input
                    type="text"
                    value={newCard.category}
                    onChange={(e) => setNewCard({ ...newCard, category: e.target.value })}
                    placeholder="如：社会学、经济学"
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">来源</label>
                  <input
                    type="text"
                    value={newCard.source}
                    onChange={(e) => setNewCard({ ...newCard, source: e.target.value })}
                    placeholder="如：作者 (年份)"
                    className="input-field"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm text-[var(--text-secondary)] mb-2 font-medium">关键词</label>
                <input
                  type="text"
                  value={newCard.keywords}
                  onChange={(e) => setNewCard({ ...newCard, keywords: e.target.value })}
                  placeholder="用逗号分隔，如：公共资源, 治理"
                  className="input-field"
                />
              </div>
              <div className="flex gap-3 justify-end pt-2">
                <button
                  onClick={() => setShowAddForm(false)}
                  className="btn-secondary"
                >
                  取消
                </button>
                <button
                  onClick={handleAddCard}
                  className="btn-primary"
                >
                  <Check className="w-4 h-4" />
                  添加
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function CardItem({ card, onDelete }: { card: Card; onDelete: (id: string) => void }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card-elevated p-4 group">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-[var(--text-primary)] truncate" style={{ fontFamily: "'Noto Serif SC', serif" }}>
            {card.title}
          </h4>
          <p className="text-sm text-[var(--text-secondary)] mt-1 line-clamp-2">
            {card.content}
          </p>
          <div className="flex items-center gap-2 mt-2">
            <span className="tag text-xs">{card.category}</span>
            {card.source && (
              <span className="text-xs text-[var(--text-muted)] truncate">{card.source}</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-2 text-[var(--text-secondary)] hover:text-[var(--accent-amber-light)] transition-colors rounded-lg hover:bg-[var(--bg-tertiary)]"
          >
            <Tag className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(card.id)}
            className="p-2 text-[var(--text-secondary)] hover:text-red-400 transition-colors rounded-lg hover:bg-[var(--bg-tertiary)]"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
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
