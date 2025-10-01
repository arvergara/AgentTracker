// Utilidades generales para la aplicación Comsulting

// Formatear números con separador de miles
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

// Formatear moneda chilena
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP',
        minimumFractionDigits: 0
    }).format(amount);
}

// Formatear fecha
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-CL', options);
}

// Mostrar notificación
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Confirmar acción
function confirmAction(message) {
    return confirm(message);
}

// Validar formulario
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

// Debounce para búsquedas
function debounce(func, wait) {
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

// Exportar datos a CSV
function exportTableToCSV(tableId, filename = 'data.csv') {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tr');
    const csv = [];
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(col => {
            rowData.push(col.textContent.trim());
        });
        csv.push(rowData.join(','));
    });
    
    const csvString = csv.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('Comsulting Admin System v1.0 cargado');
    
    // Auto-rellenar fecha actual en formularios de horas
    const fechaInput = document.getElementById('fecha');
    if (fechaInput && !fechaInput.value) {
        const today = new Date().toISOString().split('T')[0];
        fechaInput.value = today;
    }
    
    // Agregar animaciones de carga
    const cards = document.querySelectorAll('.stat-card, .feature-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
});

// Manejar errores de fetch
async function fetchWithErrorHandling(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error en la petición:', error);
        showNotification('Error al cargar los datos. Por favor, intenta nuevamente.', 'error');
        throw error;
    }
}

// Crear gráfico simple con barras
function createSimpleBarChart(data, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const maxValue = Math.max(...data.map(d => d.value));
    let html = '<div class="simple-chart">';
    
    data.forEach(item => {
        const percentage = (item.value / maxValue) * 100;
        html += `
            <div class="chart-bar">
                <div class="chart-label">${item.label}</div>
                <div class="chart-bar-container">
                    <div class="chart-bar-fill" style="width: ${percentage}%"></div>
                </div>
                <div class="chart-value">${item.value}</div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Paginación simple
class Pagination {
    constructor(items, itemsPerPage = 10) {
        this.items = items;
        this.itemsPerPage = itemsPerPage;
        this.currentPage = 1;
    }
    
    get totalPages() {
        return Math.ceil(this.items.length / this.itemsPerPage);
    }
    
    getPageItems() {
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        return this.items.slice(start, end);
    }
    
    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage++;
            return true;
        }
        return false;
    }
    
    prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            return true;
        }
        return false;
    }
    
    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.currentPage = page;
            return true;
        }
        return false;
    }
}

// Storage local helper
const LocalStorage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error guardando en localStorage:', e);
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error leyendo de localStorage:', e);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Error eliminando de localStorage:', e);
        }
    },
    
    clear: () => {
        try {
            localStorage.clear();
        } catch (e) {
            console.error('Error limpiando localStorage:', e);
        }
    }
};

// Helpers para cálculos
const Calculator = {
    // Calcular porcentaje
    percentage: (value, total) => {
        return total > 0 ? (value / total) * 100 : 0;
    },
    
    // Calcular margen
    margin: (revenue, cost) => {
        return revenue > 0 ? ((revenue - cost) / revenue) * 100 : 0;
    },
    
    // Calcular ROI
    roi: (gain, cost) => {
        return cost > 0 ? ((gain - cost) / cost) * 100 : 0;
    },
    
    // Redondear a decimales
    round: (value, decimals = 2) => {
        return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
    }
};

// Exportar para uso global
window.ComsultingUtils = {
    formatNumber,
    formatCurrency,
    formatDate,
    showNotification,
    confirmAction,
    validateForm,
    debounce,
    exportTableToCSV,
    fetchWithErrorHandling,
    createSimpleBarChart,
    Pagination,
    LocalStorage,
    Calculator
};

console.log('Utilidades Comsulting cargadas correctamente');
