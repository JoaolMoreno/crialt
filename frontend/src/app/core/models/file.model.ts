import { User } from './user.model';

export type FileCategory = 'document' | 'image' | 'plan' | 'render' | 'contract';

export interface File {
  id: string;
  original_name: string;
  stored_name: string;
  path: string;
  size: number;
  mime_type: string;
  category: FileCategory;
  tags: string[];
  project_id?: string;
  client_id?: string;
  stage_id?: string;
  description?: string;
  uploaded_by: User;
  created_at: string;
  updated_at: string;
}

