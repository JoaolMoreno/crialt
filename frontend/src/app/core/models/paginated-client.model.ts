import { Client } from './client.model';

export interface PaginatedClient {
  total: number;
  count: number;
  offset: number;
  limit: number;
  items: Client[];
}

