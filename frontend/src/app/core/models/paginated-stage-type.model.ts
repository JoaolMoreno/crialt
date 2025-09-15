import { StageType } from './stage-type.model';

export interface PaginatedStageType {
  total: number;
  count: number;
  offset: number;
  limit: number;
  items: StageType[];
}
