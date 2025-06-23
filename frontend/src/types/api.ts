
export interface User {
    id: string;
    email: string;
    username: string;
    created_at: string;
    updated_at?: string;
}

export interface LoginData {
    email: string;
    password: string;
}

export interface RegisterData extends LoginData {
    username: string;
}

// Transaction Types
export type TransactionType = "income" | "expense";

export interface TransactionData {
    amount: number;
    type: TransactionType;
    category: string;
    description: string;
}

export interface Transaction extends TransactionData {
    id: string;
    user_id: string;
    transaction_date: string;
    is_ai_categorize: boolean;
    created_at: string;
    updated_at?: string;
}

// Chat Systems
export type SenderType = "user" | "ai";

export type ConversationStatus = "active" | "archived" | "deleted";

export interface MessageData {
    content: string;
    conversation_id?: string;
}

export interface Message extends MessageData {
    id: string;
    sender_type: SenderType;
    message_index: number;
    created_at: string;
    updated_at: string;
    token_used?: number;
    response_time_ms?: number;
    ai_model?: string;
}

export interface ConversationData {
    topic?: string;
    status?: ConversationStatus;
    updated_at?: string;
}

export interface Conversation extends ConversationData {
    id: string;
    user_id: string;
    total_message: number;
    created_at: string;
}