import { Project } from './project.model';
import { File } from './file.model';
import { Task } from './task.model';
import { User } from './user.model';
import { StageStatus } from './status.model';
import {StageType} from "./stage-type.model";

export interface StageSpecificData {
  // Tipos específicos podem ser detalhados depois
  [key: string]: any;
}

export interface Stage {
  id: string;
  name: string;
  description?: string;
  order: number;
  status: StageStatus;
  planned_start_date: string;
  actual_start_date?: string;
  planned_end_date: string;
  actual_end_date?: string;
  value: number;
  specific_data?: StageSpecificData;
  progress_percentage: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  project_id: string;
  stage_type_id: string;
  created_by_id: string;
  assigned_to_id?: string;
  project?: Project;
  stage_type?: StageType;
  files?: File[];
  tasks?: Task[];
  created_by?: User;
  assigned_to?: User;
}
