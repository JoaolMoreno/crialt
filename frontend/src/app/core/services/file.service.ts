import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { File } from '../models/file.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class FileService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/files`;

  getFiles(): Observable<File[]> {
    return this.http.get<File[]>(this.apiUrl);
  }

  getFileById(id: string): Observable<File> {
    return this.http.get<File>(`${this.apiUrl}/${id}`);
  }

  uploadFile(formData: FormData): Observable<File> {
    return this.http.post<File>(this.apiUrl, formData);
  }

  deleteFile(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
