import { Project } from './project.model';
import { File } from './file.model';
import { Task } from './task.model';
import { User } from './user.model';

export type StageType =
  | 'levantamento'
  | 'briefing'
  | 'estudo_preliminar'
  | 'projeto_executivo'
  | 'assessoria_pos_projeto';

export type StageStatus =
  | 'pending'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'on_hold';

export type PaymentStatus = 'pending' | 'partial' | 'paid';

export interface StageSpecificData {
  // Tipos específicos podem ser detalhados depois
  [key: string]: any;
}

export interface Stage {
  id: string;
  name: string;
  type: StageType;
  description?: string;
  order: number;
  status: StageStatus;
  planned_start_date: string;
  actual_start_date?: string;
  planned_end_date: string;
  actual_end_date?: string;
  value: number;
  payment_status: PaymentStatus;
  specific_data: StageSpecificData;
  progress_percentage: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  project: Project;
  files: File[];
  tasks: Task[];
  created_by: User;
  assigned_to?: User;
}

