import { Client } from './client.model';
import { Stage } from './stage.model';
import { File } from './file.model';
import { User } from './user.model';
import { ProjectStatus } from './status.model';

export interface Project {
  id: string;
  name: string;
  description?: string;
  total_value: number;
  currency: string;
  start_date: string;
  estimated_end_date: string;
  actual_end_date?: string;
  status: ProjectStatus;
  work_address: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
    reference?: string;
  };
  scope: {
    total_area?: number;
    rooms_included: string[];
    technical_notes?: string;
  };
  notes?: string;
  created_at: string;
  updated_at: string;
  clients: Client[];
  stages: Stage[];
  files: File[];
  created_by: User;
}
