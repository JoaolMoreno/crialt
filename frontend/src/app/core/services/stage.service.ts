import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Stage } from '../models/stage.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class StageService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/stages`;

  getStages(): Observable<Stage[]> {
    return this.http.get<Stage[]>(this.apiUrl);
  }

  getStageById(id: string): Observable<Stage> {
    return this.http.get<Stage>(`${this.apiUrl}/${id}`);
  }

  createStage(stage: Partial<Stage>): Observable<Stage> {
    return this.http.post<Stage>(this.apiUrl, stage);
  }

  updateStage(id: string, stage: Partial<Stage>): Observable<Stage> {
    return this.http.put<Stage>(`${this.apiUrl}/${id}`, stage);
  }

  deleteStage(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
