import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface FileUpload {
  id: string;
  original_name: string;
  stored_name: string;
  path: string;
  size: number;
  mime_type: string;
  category: FileCategory;
  description?: string;
  created_at: string;
  updated_at: string;
  project_id?: string;
  client_id?: string;
  stage_id?: string;
  uploaded_by_id: string;
}

export enum FileCategory {
  DOCUMENT = 'document',
  IMAGE = 'image',
  PLAN = 'plan',
  RENDER = 'render',
  CONTRACT = 'contract'
}

export interface FileUploadResponse {
  id: string;
  original_name: string;
  stored_name: string;
  path: string;
  size: number;
  mime_type: string;
  category: FileCategory;
  description?: string;
  created_at: string;
  updated_at: string;
  project_id?: string;
  client_id?: string;
  stage_id?: string;
  uploaded_by_id: string;
}

export interface PaginatedFiles {
  total: number;
  count: number;
  offset: number;
  limit: number;
  items: FileUpload[];
}

@Injectable({
  providedIn: 'root'
})
export class FileService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/files`;

  uploadFile(file: File, projectId: string, category: FileCategory, description?: string): Observable<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    formData.append('project_id', projectId);

    if (description) {
      formData.append('description', description);
    }

    return this.http.post<FileUploadResponse>(this.baseUrl, formData, { withCredentials: true });
  }

  getFilesByProject(projectId: string): Observable<FileUpload[]> {
    return this.http.get<FileUpload[]>(`${this.baseUrl}/project/${projectId}`, { withCredentials: true });
  }

  downloadFile(fileId: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/${fileId}/download`, {
      responseType: 'blob',
      withCredentials: true
    });
  }

  deleteFile(fileId: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.baseUrl}/${fileId}`, { withCredentials: true });
  }

  getFiles(params?: Record<string, any>): Observable<PaginatedFiles> {
    let httpParams = new URLSearchParams();

    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          httpParams.append(key, params[key].toString());
        }
      });
    }

    const queryString = httpParams.toString();
    const url = queryString ? `${this.baseUrl}?${queryString}` : this.baseUrl;

    return this.http.get<PaginatedFiles>(url, { withCredentials: true });
  }

  downloadFileToDevice(fileId: string, fileName: string): void {
    this.downloadFile(fileId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        console.error('Erro ao baixar arquivo:', error);
      }
    });
  }
}
