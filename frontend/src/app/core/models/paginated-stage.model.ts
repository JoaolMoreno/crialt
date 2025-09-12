import { Stage } from './stage.model';

export interface PaginatedStage {
  total: number;
  count: number;
  offset: number;
  limit: number;
  items: Stage[];
}

