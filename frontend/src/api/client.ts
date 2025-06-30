import axios from 'axios'
import type { User, LoginData, RegisterData } from '@/types/api'
import type { Transaction, TransactionData } from '@/types/api'

const API_BASE_URL = 'http://localhost:8000'

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
})

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        // เพิ่ม auth token
        const token = localStorage.getItem("auth_token")
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }

        console.log('API Request:', config.method?.toUpperCase(), config.url)
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response Interceptor
apiClient.interceptors.response.use(
    (response) => {
        console.log('API Response:', response.status, response.config.url)
        return response
    },
    (error) => {
        // Auto logout ถ้า unauthorized
        if (error.response?.status === 401) {
            localStorage.removeItem('auth_token')
            window.location.href = '/login'
        }

        console.error('API Response: ', error.response?.status, error.config?.url)
        return Promise.reject(error)
    }
)

// Auth API 
export const authAPI = {
    // post api/auth/login
    login: (data: LoginData) =>
        apiClient.post<User>('/api/auth/login', data),

    // post api/auth/register
    register: (data: RegisterData) =>
        apiClient.post<User>('/api/auth/register', data),

    // get api/auth/me
    getCurrentUser: () =>
        apiClient.get<User>('/api/auth/me'),
} 

// Transaction API
export const transactionAPI = {
    getAll: () => apiClient.get<Transaction[]>('/api/transactions'),
    create: (data: TransactionData) => apiClient.post<Transaction>('/api/transactions', data),
    update: (id: string, data: TransactionData) => apiClient.put<Transaction>(`/api/transactions/${id}`, data),
    delete: (id: string) => apiClient.delete(`/api/transactions/${id}`)
}