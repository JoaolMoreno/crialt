import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { File } from '../models/file.model';
import { PaginatedFile } from '../models/paginated-file.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class FileService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/files`;

  private filterParams(params: Record<string, any>): Record<string, any> {
    return Object.fromEntries(
      Object.entries(params).filter(
        ([, v]) => v !== undefined && v !== null && !(typeof v === 'string' && v.trim() === '')
      )
    );
  }

  getFiles(params: Record<string, any> = {}): Observable<PaginatedFile> {
    const filteredParams = this.filterParams(params);
    const query = new URLSearchParams(filteredParams).toString();
    return this.http.get<PaginatedFile>(`${this.apiUrl}${query ? '?' + query : ''}`, { withCredentials: true });
  }

  getFileById(id: string): Observable<File> {
    return this.http.get<File>(`${this.apiUrl}/${id}`, { withCredentials: true });
  }

  uploadFile(formData: FormData): Observable<File> {
    return this.http.post<File>(this.apiUrl, formData, { withCredentials: true });
  }

  deleteFile(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, { withCredentials: true });
  }
}
