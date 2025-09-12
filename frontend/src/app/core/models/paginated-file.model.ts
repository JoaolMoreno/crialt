import { File } from './file.model';

export interface PaginatedFile {
  total: number;
  count: number;
  offset: number;
  limit: number;
  items: File[];
}

