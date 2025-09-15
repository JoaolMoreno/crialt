export interface StageType {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface StageTypeCreate {
  name: string;
  description?: string;
  is_active?: boolean;
}

export interface StageTypeUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}
