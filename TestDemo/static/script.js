/**
 * 在线刷题系统 - 前端交互脚本
 */

// 工具函数
const Utils = {
    // 防抖函数
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // 节流函数
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // 本地存储封装
    storage: {
        get(key) {
            try {
                const value = localStorage.getItem(key);
                return value ? JSON.parse(value) : null;
            } catch (e) {
                return null;
            }
        },
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (e) {
                return false;
            }
        },
        remove(key) {
            localStorage.removeItem(key);
        },
        clear() {
            localStorage.clear();
        }
    },

    // 格式化日期
    formatDate(date) {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    // 显示通知
    notify(message, type = 'info') {
        const colors = {
            success: 'bg-success',
            error: 'bg-danger',
            warning: 'bg-warning',
            info: 'bg-info'
        };

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white ${colors[type]} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }

        container.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
};

// 刷题相关
const Practice = {
    currentQuestion: null,
    answeredQuestions: [],
    stats: {
        total: 0,
        correct: 0,
        wrong: 0,
        accuracy: 0
    },

    async init() {
        const checkRes = await fetch('/api/import/check');
        const checkData = await checkRes.json();

        if (!checkData.imported) {
            this.showEmpty('题库未导入，请点击右上角"导入题库"按钮');
            return false;
        }

        await this.loadStats();
        return true;
    },

    async loadStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            if (data.success) {
                this.stats = data.stats;
                this.updateStatsUI();
            }
        } catch (e) {
            console.error('加载统计失败:', e);
        }
    },

    updateStatsUI() {
        // 更新正确率
        document.querySelectorAll('.correct-rate').forEach(el => {
            el.textContent = this.stats.accuracy + '%';
        });

        // 更新错题数
        document.querySelectorAll('.wrong-count').forEach(el => {
            el.textContent = this.stats.wrong_count;
        });
    },

    showEmpty(message) {
        document.getElementById('questionArea').innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <h5>${message}</h5>
            </div>
        `;
    }
};

// 错题本相关
const Wrongbook = {
    questions: [],

    async load() {
        try {
            const res = await fetch('/api/wrongbook');
            const data = await res.json();
            if (data.success) {
                this.questions = data.questions;
                this.render();
            }
        } catch (e) {
            console.error('加载错题本失败:', e);
        }
    },

    render() {
        const container = document.getElementById('wrongbookList');
        if (!container) return;

        if (this.questions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-check-circle"></i>
                    <h5 class="text-muted">太棒了！没有错题！</h5>
                </div>
            `;
            return;
        }

        // 渲染错题列表
        // ... 具体渲染逻辑
    }
};

// 导出到全局
window.Utils = Utils;
window.Practice = Practice;
window.Wrongbook = Wrongbook;

// 题库总览相关（页面内嵌模式）
const QuestionOverview = {
    allData: null,
    currentType: 'all',
    isOverviewMode: false,

    async showQuestionOverview() {
        this.currentType = 'all';
        this.isOverviewMode = true;

        // 渲染题库总览界面到主内容区
        document.getElementById('questionArea').innerHTML = `
            <div class="p-4">
                <!-- 题库总览头部 -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h4 class="mb-0">
                        <i class="bi bi-collection me-2 text-primary"></i>题库总览
                    </h4>
                    <button class="btn btn-outline-secondary btn-sm" onclick="QuestionOverview.exitOverview()">
                        <i class="bi bi-arrow-left me-1"></i>返回刷题
                    </button>
                </div>
                <!-- 题型选择标签 -->
                <div class="mb-4">
                    <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="overviewType" id="overviewAll" value="all" checked>
                        <label class="btn btn-outline-primary" for="overviewAll">
                            <i class="bi bi-list-ul me-1"></i>全部题型 <span class="badge bg-primary" id="overviewAllCount">0</span>
                        </label>
                        <input type="radio" class="btn-check" name="overviewType" id="overviewSingle" value="single">
                        <label class="btn btn-outline-success" for="overviewSingle">
                            <i class="bi bi-circle me-1"></i>单选题 <span class="badge bg-success" id="overviewSingleCount">0</span>
                        </label>
                        <input type="radio" class="btn-check" name="overviewMulti" id="overviewMulti" value="multi">
                        <label class="btn btn-outline-warning" for="overviewMulti">
                            <i class="bi bi-check2-square me-1"></i>多选题 <span class="badge bg-warning text-dark" id="overviewMultiCount">0</span>
                        </label>
                        <input type="radio" class="btn-check" name="overviewType" id="overviewJudge" value="judge">
                        <label class="btn btn-outline-info" for="overviewJudge">
                            <i class="bi bi-toggle-on me-1"></i>判断题 <span class="badge bg-info" id="overviewJudgeCount">0</span>
                        </label>
                    </div>
                </div>
                <!-- 题目列表 -->
                <div class="overview-content" id="overviewContent">
                    <div class="text-center text-muted py-5">
                        <div class="spinner-border text-primary" role="status"></div>
                        <p class="mt-2">正在加载题库...</p>
                    </div>
                </div>
            </div>
        `;

        // 绑定题型切换事件
        document.querySelectorAll('input[name="overviewType"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.changeType(e.target.value);
            });
        });

        if (!this.allData) {
            await this.loadAllQuestions();
        }
        this.updateCounts();
        this.renderQuestions();
    },

    exitOverview() {
        this.isOverviewMode = false;
        this.allData = null;
        // 重新加载刷题界面
        if (window.Practice && Practice.init) {
            Practice.init().then(ready => {
                if (ready) {
                    Practice.loadNextQuestion();
                }
            });
        }
    },

    async loadAllQuestions() {
        try {
            const res = await fetch('/api/questions/all');
            const data = await res.json();
            if (data.success) {
                this.allData = data;
            }
        } catch (e) {
            console.error('加载题库失败:', e);
            document.getElementById('overviewContent').innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>加载题库失败，请重试
                </div>
            `;
        }
    },

    updateCounts() {
        if (!this.allData) return;
        const byType = this.allData.by_type;
        document.getElementById('overviewAllCount').textContent = this.allData.count;
        document.getElementById('overviewSingleCount').textContent = byType.single.count;
        document.getElementById('overviewMultiCount').textContent = byType.multi.count;
        document.getElementById('overviewJudgeCount').textContent = byType.judge.count;
    },

    changeType(type) {
        this.currentType = type;
        this.renderQuestions();
    },

    renderQuestions() {
        if (!this.allData) return;

        const byType = this.allData.by_type;
        let questions = [];

        if (this.currentType === 'all') {
            questions = [
                ...byType.single.questions,
                ...byType.multi.questions,
                ...byType.judge.questions
            ];
        } else {
            questions = byType[this.currentType].questions;
        }

        const container = document.getElementById('overviewContent');

        if (questions.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="bi bi-inbox display-4"></i>
                    <h5 class="mt-3">该题型暂无题目</h5>
                </div>
            `;
            return;
        }

        const typeColors = {
            'single': { badge: 'bg-success', icon: 'bi-circle', label: '单选题' },
            'multi': { badge: 'bg-warning text-dark', icon: 'bi-check2-square', label: '多选题' },
            'judge': { badge: 'bg-info', icon: 'bi-toggle-on', label: '判断题' }
        };

        let html = '<div class="overview-list">';

        questions.forEach((q, index) => {
            const typeInfo = typeColors[q.type] || typeColors.single;
            const options = q.options || {};

            let optionsHtml = '';
            if (q.type === 'judge') {
                optionsHtml = `
                    <div class="row g-2 mb-3">
                        <div class="col-6">
                            <div class="option-card ${q.answer === 'A' ? 'correct' : ''}">
                                <span class="option-key">A</span>
                                <span class="option-value">${options['A'] || '正确'}</span>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="option-card ${q.answer === 'B' ? 'correct' : ''}">
                                <span class="option-key">B</span>
                                <span class="option-value">${options['B'] || '错误'}</span>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                const optionEntries = Object.entries(options);
                optionsHtml = '<div class="options-grid mb-3">';
                optionEntries.forEach(([key, value]) => {
                    const isCorrect = q.answer.toUpperCase().includes(key.toUpperCase());
                    optionsHtml += `
                        <div class="option-card ${isCorrect ? 'correct' : ''}">
                            <span class="option-key">${key}</span>
                            <span class="option-value">${value}</span>
                        </div>
                    `;
                });
                optionsHtml += '</div>';
            }

            html += `
                <div class="question-item mb-4 p-4 border rounded bg-white shadow-sm" data-type="${q.type}">
                    <div class="d-flex align-items-start mb-3">
                        <span class="badge ${typeInfo.badge} me-2">
                            <i class="${typeInfo.icon} me-1"></i>${typeInfo.label}
                        </span>
                        <span class="text-muted small">#${q.id}</span>
                    </div>
                    <div class="question-stem mb-3">
                        <strong>${index + 1}.</strong> ${q.content}
                    </div>
                    ${optionsHtml}
                    <div class="answer-section mt-3 p-3 bg-light rounded">
                        <div class="d-flex align-items-center mb-2">
                            <i class="bi bi-check-circle-fill text-success me-2"></i>
                            <strong>正确答案：</strong>
                            <span class="badge bg-success ms-2">${q.answer}</span>
                        </div>
                        ${q.explanation ? `
                            <div class="explanation mt-2">
                                <div class="d-flex align-items-center mb-1">
                                    <i class="bi bi-lightbulb-fill text-warning me-2"></i>
                                    <strong>解析：</strong>
                                </div>
                                <p class="mb-0 text-muted small">${q.explanation}</p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
    }
};

window.QuestionOverview = QuestionOverview;
window.showQuestionOverview = () => QuestionOverview.showQuestionOverview();
