import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface StageType {
  id: string;
  name: string;
  description?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface PaginatedStageType {
  total: number;
  count: number;
  offset: number;
  limit: number;
  items: StageType[];
}

@Injectable({ providedIn: 'root' })
export class StageTypeService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/stage-types`;

  getStageTypes(params: Record<string, any> = {}): Observable<PaginatedStageType> {
    const query = new URLSearchParams(params).toString();
    return this.http.get<PaginatedStageType>(`${this.apiUrl}${query ? '?' + query : ''}`, { withCredentials: true });
  }

  getActiveStageTypes(): Observable<StageType[]> {
    return this.http.get<StageType[]>(`${this.apiUrl}/active`, { withCredentials: true });
  }
}

