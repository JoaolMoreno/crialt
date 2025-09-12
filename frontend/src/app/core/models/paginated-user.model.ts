import { User } from './user.model';

export interface PaginatedUser {
  total: number;
  count: number;
  offset: number;
  limit: number;
  items: User[];
}

