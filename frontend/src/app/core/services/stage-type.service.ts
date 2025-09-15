import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PaginatedStageType } from '../models/paginated-stage-type.model';
import { environment } from '../../environments/environment';
import {StageType, StageTypeCreate, StageTypeUpdate} from "../models/stage-type.model";

@Injectable({ providedIn: 'root' })
export class StageTypeService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/stage-types`;

  private filterParams(params: Record<string, any>): Record<string, any> {
    return Object.fromEntries(
      Object.entries(params).filter(
        ([, v]) => v !== undefined && v !== null && !(typeof v === 'string' && v.trim() === '')
      )
    );
  }

  getStageTypes(params: Record<string, any> = {}): Observable<PaginatedStageType> {
    const filteredParams = this.filterParams(params);
    const query = new URLSearchParams(filteredParams).toString();
    return this.http.get<PaginatedStageType>(`${this.apiUrl}${query ? '?' + query : ''}`, { withCredentials: true });
  }

  getActiveStageTypes(): Observable<StageType[]> {
    return this.http.get<StageType[]>(`${this.apiUrl}/active`, { withCredentials: true });
  }

  getStageTypeById(id: string): Observable<StageType> {
    return this.http.get<StageType>(`${this.apiUrl}/${id}`, { withCredentials: true });
  }

  createStageType(stageType: StageTypeCreate): Observable<StageType> {
    return this.http.post<StageType>(this.apiUrl, stageType, { withCredentials: true });
  }

  updateStageType(id: string, stageType: StageTypeUpdate): Observable<StageType> {
    return this.http.put<StageType>(`${this.apiUrl}/${id}`, stageType, { withCredentials: true });
  }

  deleteStageType(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, { withCredentials: true });
  }
}
