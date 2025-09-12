import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Stage } from '../models/stage.model';
import { PaginatedStage } from '../models/paginated-stage.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class StageService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/stages`;

  private filterParams(params: Record<string, any>): Record<string, any> {
    return Object.fromEntries(
      Object.entries(params).filter(
        ([, v]) => v !== undefined && v !== null && !(typeof v === 'string' && v.trim() === '')
      )
    );
  }

  getStages(params: Record<string, any> = {}): Observable<PaginatedStage> {
    const filteredParams = this.filterParams(params);
    const query = new URLSearchParams(filteredParams).toString();
    return this.http.get<PaginatedStage>(`${this.apiUrl}${query ? '?' + query : ''}`, { withCredentials: true });
  }

  getStageById(id: string): Observable<Stage> {
    return this.http.get<Stage>(`${this.apiUrl}/${id}`, { withCredentials: true });
  }

  createStage(stage: Partial<Stage>): Observable<Stage> {
    return this.http.post<Stage>(this.apiUrl, stage, { withCredentials: true });
  }

  updateStage(id: string, stage: Partial<Stage>): Observable<Stage> {
    return this.http.put<Stage>(`${this.apiUrl}/${id}`, stage, { withCredentials: true });
  }

  deleteStage(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, { withCredentials: true });
  }
}
