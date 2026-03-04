/**
 * API Utility for Backend Communication
 */

const API_BASE_URL = '/api/v1';

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'An unknown error occurred' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    return response.json();
}

export const api = {
    // Dashboard & Stats
    async getDashboardStats() {
        return handleResponse(await fetch(`${API_BASE_URL}/dashboard/stats`));
    },
    async getERIHistory() {
        return handleResponse(await fetch(`${API_BASE_URL}/dashboard/eri-history`));
    },
    async getPipelineStatus() {
        return handleResponse(await fetch(`${API_BASE_URL}/dashboard/pipeline`));
    },
    async getSourceHealth() {
        return handleResponse(await fetch(`${API_BASE_URL}/dashboard/source-health`));
    },

    // Data Sources
    async getDataSources() {
        return handleResponse(await fetch(`${API_BASE_URL}/sources/`));
    },
    async testDataSource(id: string) {
        return handleResponse(await fetch(`${API_BASE_URL}/sources/${id}/test`, { method: 'POST' }));
    },
    async fetchFromSource(id: string) {
        return handleResponse(await fetch(`${API_BASE_URL}/sources/${id}/fetch`, { method: 'POST' }));
    },
    async toggleSource(id: string) {
        return handleResponse(await fetch(`${API_BASE_URL}/sources/${id}/toggle`, { method: 'PATCH' }));
    },

    // Articles & Content
    async getArticles() {
        return handleResponse(await fetch(`${API_BASE_URL}/articles/`));
    },
    async getContents() {
        // Map contents to articles endpoint
        return handleResponse(await fetch(`${API_BASE_URL}/articles/`));
    },
    async createContent(data: any) {
        return handleResponse(await fetch(`${API_BASE_URL}/articles/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: JSON.stringify(data),
        }));
    },

    // ERI Assessments
    async getERIAssessments() {
        return handleResponse(await fetch(`${API_BASE_URL}/eri/`));
    },
    async getCurrentERI() {
        return handleResponse(await fetch(`${API_BASE_URL}/eri/current`));
    },
    async createERIAssessment(data: any) {
        return handleResponse(await fetch(`${API_BASE_URL}/eri/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        }));
    },

    // Risk Assessments
    async getRiskAssessments() {
        return handleResponse(await fetch(`${API_BASE_URL}/risk/`));
    },
    async assessArticleRisk(articleId: string) {
        return handleResponse(await fetch(`${API_BASE_URL}/risk/assess/${articleId}`, { method: 'POST' }));
    },
    async getSafeModeStatus() {
        return handleResponse(await fetch(`${API_BASE_URL}/risk/config/safe-mode`));
    },
    async toggleSafeMode(enabled: boolean) {
        return handleResponse(await fetch(`${API_BASE_URL}/risk/config/safe-mode?enabled=${enabled}`, { method: 'PUT' }));
    },

    // Video Production
    async getVideoJobs(status?: string, scriptId?: string) {
        let url = `${API_BASE_URL}/videos/jobs`;
        const params = new URLSearchParams();
        if (status) params.append('status', status);
        if (scriptId) params.append('script_id', scriptId);
        if (params.toString()) url += `?${params.toString()}`;
        return handleResponse(await fetch(url));
    },
    async createVideoJob(data: { script_id: string; priority?: number; resolution?: string }) {
        return handleResponse(await fetch(`${API_BASE_URL}/videos/jobs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        }));
    },
    async cancelVideoJob(jobId: string) {
        return handleResponse(await fetch(`${API_BASE_URL}/videos/jobs/${jobId}/cancel`, { method: 'POST' }));
    },
    async getVideoPipelineStatus() {
        return handleResponse(await fetch(`${API_BASE_URL}/videos/pipeline/status`));
    },

    // Automation
    async getAutomationSchedules() {
        return handleResponse(await fetch(`${API_BASE_URL}/automation/schedules`));
    },
    async createAutomationSchedule(data: any) {
        return handleResponse(await fetch(`${API_BASE_URL}/automation/schedules`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        }));
    },
    async updateAutomationSchedule(id: string, data: any) {
        return handleResponse(await fetch(`${API_BASE_URL}/automation/schedules/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        }));
    },
    async deleteAutomationSchedule(id: string) {
        return handleResponse(await fetch(`${API_BASE_URL}/automation/schedules/${id}`, { method: 'DELETE' }));
    },
    async runAutomationScheduleNow(id: string) {
        return handleResponse(await fetch(`${API_BASE_URL}/automation/schedules/${id}/run`, { method: 'POST' }));
    },

    // System Health
    async getSystemHealth() {
        try {
            const health = await handleResponse<any>(await fetch(`${API_BASE_URL.replace('/v1', '')}/health`));
            return {
                overall: health.status === 'healthy' ? 'healthy' : 'degraded',
                services: [
                    { name: 'Core API', status: health.status === 'healthy' ? 'up' : 'down', responseTime: 5 },
                    { name: 'Database', status: 'up', responseTime: 2 }, // Simplified for now
                    { name: 'Environment', status: 'up', info: health.environment }
                ],
                lastCheck: new Date().toISOString()
            };
        } catch (error) {
            return {
                overall: 'critical',
                services: [
                    { name: 'Core API', status: 'down', responseTime: 0 }
                ],
                lastCheck: new Date().toISOString()
            };
        }
    }
};
