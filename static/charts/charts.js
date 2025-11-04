/**
 * 图表功能JavaScript工具
 * 提供图表创建和数据处理功能
 */

class ChartManager {
    constructor() {
        this.colorArray = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ];
    }
    
    /**
     * 创建饼图
     * @param {string} canvasId - Canvas元素ID
     * @param {Array} data - 图表数据
     * @param {Object} options - 图表选项
     */
    createPieChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.map(item => item.label),
                datasets: [{
                    data: data.map(item => item.value),
                    backgroundColor: this.colorArray.slice(0, data.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                ...options
            }
        });
    }
    
    /**
     * 创建柱状图
     * @param {string} canvasId - Canvas元素ID
     * @param {Array} data - 图表数据
     * @param {Object} options - 图表选项
     */
    createBarChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.label),
                datasets: [{
                    label: options.label || '数量',
                    data: data.map(item => item.value),
                    backgroundColor: options.backgroundColor || '#4ECDC4',
                    borderColor: options.borderColor || '#26de81',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${options.label || '数量'}: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                ...options
            }
        });
    }
    
    /**
     * 创建水平柱状图
     * @param {string} canvasId - Canvas元素ID
     * @param {Array} data - 图表数据
     * @param {Object} options - 图表选项
     */
    createHorizontalBarChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.label),
                datasets: [{
                    label: options.label || '数量',
                    data: data.map(item => item.value),
                    backgroundColor: options.backgroundColor || '#96CEB4',
                    borderColor: options.borderColor || '#68d391',
                    borderWidth: 2,
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${options.label || '数量'}: ${context.parsed.x}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                },
                ...options
            }
        });
    }
    
    /**
     * 创建折线图
     * @param {string} canvasId - Canvas元素ID
     * @param {Array} data - 图表数据
     * @param {Object} options - 图表选项
     */
    createLineChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.date || item.label),
                datasets: [{
                    label: options.label || '趋势',
                    data: data.map(item => item.value),
                    borderColor: options.borderColor || '#FF6B6B',
                    backgroundColor: options.backgroundColor || 'rgba(255, 107, 107, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: options.borderColor || '#FF6B6B',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `${options.label || '数值'}: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                ...options
            }
        });
    }
    
    /**
     * 获取图表数据
     * @param {string} chartType - 图表类型
     * @returns {Promise} - 数据Promise
     */
    async fetchChartData(chartType) {
        try {
            const response = await fetch(`/charts/data/${chartType}/`);
            const data = await response.json();
            
            if (data.status === 'success') {
                return data.data;
            } else {
                console.error('获取图表数据失败:', data.message);
                return null;
            }
        } catch (error) {
            console.error('获取图表数据时发生错误:', error);
            return null;
        }
    }
    
    /**
     * 防抖函数
     * @param {Function} func - 函数
     * @param {number} wait - 等待时间
     * @returns {Function} - 防抖函数
     */
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
    }
}

// 初始化图表管理器
const chartManager = new ChartManager();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('图表功能已加载');
});
