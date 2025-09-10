export interface User {
  id: string;
  name: string;
  email: string;
  password_hash: string;
  role: 'admin' | 'architect' | 'assistant';
  avatar?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

