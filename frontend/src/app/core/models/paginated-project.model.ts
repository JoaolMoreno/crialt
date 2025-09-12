import { Project } from './project.model';

export interface PaginatedProject {
    total: number;
    count: number;
    offset: number;
    limit: number;
    items: Project[];
}
