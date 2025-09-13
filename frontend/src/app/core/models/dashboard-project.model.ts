import { Project } from './project.model';

export interface DashboardProject extends Project {
  client_name: string | null;
}

