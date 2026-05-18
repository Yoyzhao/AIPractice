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
