# Frontend Development Guide
## Complete React + TypeScript Setup Guide

---

## 🚀 **Technology Stack**

### **Core Framework:**
- **React 18** - Latest stable version with Concurrent Features
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool and development server

### **UI & Styling:**
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - High-quality React components
- **Lucide React** - Beautiful icons

### **State Management:**
- **Zustand** - Lightweight global state management
- **React Query (TanStack Query)** - Server state management and caching
- **React Hook Form** - Form handling with validation

### **API & Networking:**
- **Axios** - HTTP client with interceptors
- **TypeScript Interfaces** - Type-safe API calls

---

## 📁 **Project Structure**

```
frontend/
├── public/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── forms/          # Form components
│   │   └── layout/         # Layout components
│   ├── pages/              # Page components
│   │   ├── auth/           # Login, Register
│   │   ├── dashboard/      # Main dashboard
│   │   ├── transactions/   # Transaction management
│   │   └── chat/           # AI chat interface
│   ├── hooks/              # Custom React hooks
│   ├── store/              # Zustand stores
│   ├── api/                # API client and types
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Helper functions
│   └── styles/             # Global styles
├── package.json
└── tsconfig.json
```

---

## 🛠 **Setup Commands**

### **1. Create Project:**
```bash
# Using Vite (Recommended - faster)
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install

# OR using Create React App
npx create-react-app frontend --template typescript
cd frontend
```

### **2. Install Dependencies:**
```bash
# UI Framework
npm install tailwindcss @tailwindcss/typography
npx tailwindcss init -p

# shadcn/ui setup
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card dialog

# State Management
npm install zustand @tanstack/react-query

# API & Forms
npm install axios react-hook-form @hookform/resolvers zod

# Icons & Utils
npm install lucide-react clsx tailwind-merge

# Development tools
npm install -D @types/node
```

### **3. Configure Tailwind CSS:**
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

## 🎯 **API Integration Setup**

### **Type Definitions (src/types/api.ts):**
```typescript
// User Types
export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
  updated_at: string;
}

// Transaction Types
export interface Transaction {
  id: string;
  user_id: string;
  amount: number;
  type: 'income' | 'expense';
  category: string;
  description: string;
  note?: string;
  transaction_date: string;
  is_ai_categorize: boolean;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  amount: number;
  type: 'income' | 'expense';
  category: string;
  description: string;
  note?: string;
  transaction_date: string;
}

// Chat Types
export interface Message {
  id: string;
  conversation_id: string;
  content: string;
  sender_type: 'user' | 'ai';
  message_index: number;
  token_used?: number;
  response_time_ms?: number;
  ai_model?: string;
  created_at: string;
  updated_at?: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  topic: string;
  total_message: number;
  status: 'active' | 'archived' | 'deleted';
  created_at: string;
  updated_at?: string;
}

// API Response Types
export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationInfo;
}
```

### **API Client (src/api/client.ts):**
```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // For session-based auth
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

## 🗄 **State Management**

### **Auth Store (src/store/authStore.ts):**
```typescript
import { create } from 'zustand';
import { User } from '../types/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  
  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      // API call implementation
      const response = await apiClient.post('/auth/login', { email, password });
      const user = response.data;
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('auth_token');
    set({ user: null, isAuthenticated: false });
  },
  
  setUser: (user: User) => {
    set({ user, isAuthenticated: true });
  },
}));
```

---

## 🎨 **Component Examples**

### **Button Component (using shadcn/ui):**
```typescript
// src/components/ui/button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary';
  size?: 'default' | 'sm' | 'lg';
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => {
    return (
      <button
        className={clsx(
          'inline-flex items-center justify-center rounded-md font-medium transition-colors',
          {
            'bg-blue-600 text-white hover:bg-blue-700': variant === 'default',
            'bg-red-600 text-white hover:bg-red-700': variant === 'destructive',
            'border border-gray-300 hover:bg-gray-50': variant === 'outline',
            'h-10 px-4 py-2': size === 'default',
            'h-9 px-3': size === 'sm',
            'h-11 px-8': size === 'lg',
          },
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);

export { Button };
```

### **Transaction Form Component:**
```typescript
// src/components/forms/TransactionForm.tsx
import { useForm } from 'react-hook-form';
import { TransactionCreate } from '../../types/api';
import { Button } from '../ui/button';

interface TransactionFormProps {
  onSubmit: (data: TransactionCreate) => void;
  isLoading?: boolean;
}

export function TransactionForm({ onSubmit, isLoading }: TransactionFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<TransactionCreate>();

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">
          จำนวนเงิน
        </label>
        <input
          type="number"
          step="0.01"
          {...register('amount', { required: 'กรุณาใส่จำนวนเงิน' })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        />
        {errors.amount && (
          <p className="text-red-500 text-sm">{errors.amount.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          ประเภท
        </label>
        <select
          {...register('type', { required: 'กรุณาเลือกประเภท' })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        >
          <option value="">เลือกประเภท</option>
          <option value="income">รายรับ</option>
          <option value="expense">รายจ่าย</option>
        </select>
      </div>

      <Button type="submit" disabled={isLoading}>
        {isLoading ? 'กำลังบันทึก...' : 'บันทึก'}
      </Button>
    </form>
  );
}
```

---

## 🔧 **Development Best Practices**

### **Performance Optimization:**
- Use `React.memo()` for expensive components
- Implement lazy loading with `React.lazy()`
- Use `useMemo()` and `useCallback()` for expensive calculations
- Optimize bundle size with code splitting

### **Error Handling:**
- Implement Error Boundaries
- Use React Query for automatic retry and error states
- Provide user-friendly error messages
- Log errors for debugging

### **Accessibility:**
- Use semantic HTML elements
- Implement proper ARIA labels
- Ensure keyboard navigation
- Test with screen readers

### **Testing Strategy:**
- Unit tests for utility functions
- Component tests with React Testing Library
- Integration tests for user flows
- E2E tests for critical paths

---

*Document Type: Frontend Development Guide*  
*Version: 1.0*  
*Created: 21 มิถุนายน 2568*  
*Scope: Complete frontend setup and best practices*  
*Status: Ready for implementation*