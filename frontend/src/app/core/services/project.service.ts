import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Project } from '../models/project.model';
import { PaginatedProject } from '../models/paginated-project.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ProjectService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/projects`;

  private filterParams(params: Record<string, any>): Record<string, any> {
    return Object.fromEntries(
      Object.entries(params).filter(
        ([, v]) => v !== undefined && v !== null && !(typeof v === 'string' && v.trim() === '')
      )
    );
  }

  getProjects(params: Record<string, any> = {}): Observable<PaginatedProject> {
    const filteredParams = this.filterParams(params);
    const query = new URLSearchParams(filteredParams).toString();
    return this.http.get<PaginatedProject>(`${this.apiUrl}${query ? '?' + query : ''}`, { withCredentials: true });
  }

  getProjectById(id: string): Observable<Project> {
    return this.http.get<Project>(`${this.apiUrl}/${id}`, { withCredentials: true });
  }

  createProject(project: Partial<Project>): Observable<Project> {
    return this.http.post<Project>(this.apiUrl, project, { withCredentials: true });
  }

  updateProject(id: string, project: Partial<Project>): Observable<Project> {
    return this.http.put<Project>(`${this.apiUrl}/${id}`, project, { withCredentials: true });
  }

  deleteProject(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, { withCredentials: true });
  }

  exportProjects(format: 'pdf' | 'excel'): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/export?format=${format}`, { responseType: 'blob', withCredentials: true });
  }

  updateProjectsStatus(ids: string[], status: string): Observable<void> {
    return this.http.put<void>(`${this.apiUrl}/batch-status`, { ids, status }, { withCredentials: true });
  }

  getProjectTimeline(id: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}/timeline`, { withCredentials: true });
  }
}
