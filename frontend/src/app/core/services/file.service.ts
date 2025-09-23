import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpEventType, HttpRequest } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
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
  VIDEO = 'video',
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

export interface ChunkedUploadInitiate {
  filename: string;
  total_chunks: number;
  chunk_size: number;
  total_size: number;
  file_checksum?: string;
  mime_type?: string;
  category?: string;
  project_id?: string;
  client_id?: string;
  stage_id?: string;
  description?: string;
}

export interface ChunkedUploadResponse {
  upload_id: string;
  expires_at: string;
  uploaded_chunks: number[];
}

export interface ChunkUploadResponse {
  chunk_number: number;
  received: boolean;
  upload_progress: number;
  uploaded_chunks: number[];
}

export interface ChunkedUploadStatus {
  upload_id: string;
  filename: string;
  total_chunks: number;
  uploaded_chunks: number[];
  progress: number;
  is_completed: boolean;
  final_file_id?: string;
  created_at: string;
  expires_at: string;
}

export interface ChunkedUploadComplete {
  upload_id: string;
  final_file_id: string;
  message: string;
}

export interface UploadProgress {
  uploadId: string;
  filename: string;
  progress: number;
  status: 'uploading' | 'completed' | 'error' | 'cancelled';
  error?: string;
  speed?: number;
  estimatedTimeRemaining?: number;
}

@Injectable({
  providedIn: 'root'
})
export class FileService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/files`;
  private readonly chunkedBaseUrl = `${environment.apiUrl}/files/chunked`;

  // Controle de uploads ativos
  private activeUploads = new Map<string, BehaviorSubject<UploadProgress>>();
  private uploadControllers = new Map<string, AbortController>();

  // Configurações
  private readonly CHUNK_SIZE = 5 * 1024 * 1024; // 5MB por chunk
  private readonly MAX_CONCURRENT_CHUNKS = 3;
  private readonly RETRY_ATTEMPTS = 3;

  // Métodos originais do FileService
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

  updateFile(fileId: string, data: Partial<FileUpload>): Observable<FileUpload> {
    return this.http.put<FileUpload>(`${this.baseUrl}/${fileId}`, data, { withCredentials: true });
  }

  downloadFilesByIds(fileIds: string[]): Observable<Blob> {
    return this.http.post(`${this.baseUrl}/download`, { file_ids: fileIds }, {
      responseType: 'blob',
      withCredentials: true
    });
  }

  /**
   * Inicia um upload de arquivo grande dividido em chunks
   */
  uploadLargeFile(
    file: File,
    projectId?: string,
    clientId?: string,
    stageId?: string,
    category?: string,
    description?: string
  ): Observable<UploadProgress> {
    const totalChunks = Math.ceil(file.size / this.CHUNK_SIZE);
    const uploadId = this.generateUploadId();

    const progressSubject = new BehaviorSubject<UploadProgress>({
      uploadId,
      filename: file.name,
      progress: 0,
      status: 'uploading',
      speed: 0,
      estimatedTimeRemaining: 0
    });

    this.activeUploads.set(uploadId, progressSubject);

    // Controller para cancelamento
    const controller = new AbortController();
    this.uploadControllers.set(uploadId, controller);

    // Iniciar processo de upload
    this.startChunkedUpload(file, uploadId, progressSubject, controller, {
      project_id: projectId,
      client_id: clientId,
      stage_id: stageId,
      category,
      description
    });

    return progressSubject.asObservable();
  }

  /**
   * Cancela um upload em andamento
   */
  cancelUpload(uploadId: string): Observable<any> {
    const controller = this.uploadControllers.get(uploadId);
    if (controller) {
      controller.abort();
      this.uploadControllers.delete(uploadId);
    }

    const progressSubject = this.activeUploads.get(uploadId);
    if (progressSubject) {
      progressSubject.next({
        ...progressSubject.value,
        status: 'cancelled'
      });
      this.activeUploads.delete(uploadId);
    }

    return this.http.delete(`${this.chunkedBaseUrl}/${uploadId}`, { withCredentials: true });
  }

  /**
   * Retorna o progresso de um upload específico
   */
  getUploadProgress(uploadId: string): Observable<UploadProgress> | null {
    const progressSubject = this.activeUploads.get(uploadId);
    return progressSubject ? progressSubject.asObservable() : null;
  }

  /**
   * Lista todos os uploads ativos
   */
  getActiveUploads(): UploadProgress[] {
    return Array.from(this.activeUploads.values()).map(subject => subject.value);
  }

  private async startChunkedUpload(
    file: File,
    uploadId: string,
    progressSubject: BehaviorSubject<UploadProgress>,
    controller: AbortController,
    metadata: any
  ) {
    try {
      const totalChunks = Math.ceil(file.size / this.CHUNK_SIZE);

      // Calcular checksum do arquivo completo para validação
      const fileChecksum = await this.calculateFileChecksum(file);

      // 1. Iniciar upload
      const initData: ChunkedUploadInitiate = {
        filename: file.name,
        total_chunks: totalChunks,
        chunk_size: this.CHUNK_SIZE,
        total_size: file.size,
        mime_type: file.type,
        file_checksum: fileChecksum, // Adicionar checksum
        ...metadata
      };

      const initResponse = await this.initiateUpload(initData).toPromise();
      if (!initResponse) throw new Error('Falha ao iniciar upload');

      const actualUploadId = initResponse.upload_id;

      // 2. Upload dos chunks
      const startTime = Date.now();
      const uploadedChunks = new Set(initResponse.uploaded_chunks);

      await this.uploadChunksWithConcurrency(
        file,
        actualUploadId,
        totalChunks,
        uploadedChunks,
        progressSubject,
        controller,
        startTime
      );

      // 3. Finalizar upload com validação de checksum
      if (!controller.signal.aborted) {
        const completeResponse = await this.completeUpload(actualUploadId).toPromise();

        progressSubject.next({
          ...progressSubject.value,
          progress: 100,
          status: 'completed'
        });
      }

    } catch (error: any) {
      progressSubject.next({
        ...progressSubject.value,
        status: 'error',
        error: error.message || 'Erro no upload'
      });
    } finally {
      this.cleanup(uploadId);
    }
  }

  /**
   * Calcula o checksum SHA-256 do arquivo completo
   */
  private async calculateFileChecksum(file: File): Promise<string> {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private async uploadChunksWithConcurrency(
    file: File,
    uploadId: string,
    totalChunks: number,
    uploadedChunks: Set<number>,
    progressSubject: BehaviorSubject<UploadProgress>,
    controller: AbortController,
    startTime: number
  ) {
    const chunksToUpload: number[] = [];
    for (let i = 1; i <= totalChunks; i++) {
      if (!uploadedChunks.has(i)) {
        chunksToUpload.push(i);
      }
    }

    let chunkIndex = 0;
    const activePromises: Promise<void>[] = [];
    const failedChunks: number[] = [];

    while (chunkIndex < chunksToUpload.length && !controller.signal.aborted) {
      // Controlar concorrência
      while (activePromises.length < this.MAX_CONCURRENT_CHUNKS && chunkIndex < chunksToUpload.length) {
        const chunkNumber = chunksToUpload[chunkIndex++];

        const promise = this.uploadSingleChunkWithRetry(
          file,
          uploadId,
          chunkNumber,
          controller
        ).then(() => {
          uploadedChunks.add(chunkNumber);
          this.updateProgress(progressSubject, uploadedChunks.size, totalChunks, startTime);
        }).catch((error) => {
          console.error(`Falha no chunk ${chunkNumber} após tentativas:`, error);
          failedChunks.push(chunkNumber);
        }).finally(() => {
          const index = activePromises.indexOf(promise);
          if (index > -1) activePromises.splice(index, 1);
        });

        activePromises.push(promise);
      }

      // Aguardar pelo menos um chunk terminar
      if (activePromises.length > 0) {
        await Promise.race(activePromises);
      }
    }

    // Aguardar todos os chunks restantes
    await Promise.all(activePromises);

    // Verificar se todos os chunks foram enviados com sucesso
    if (failedChunks.length > 0) {
      throw new Error(`Falha ao enviar chunks: ${failedChunks.join(', ')}`);
    }

    // Verificar integridade antes de finalizar
    const expectedChunks = Array.from({length: totalChunks}, (_, i) => i + 1);
    const uploadedArray = Array.from(uploadedChunks).sort((a, b) => a - b);

    if (JSON.stringify(expectedChunks) !== JSON.stringify(uploadedArray)) {
      const missing = expectedChunks.filter(chunk => !uploadedChunks.has(chunk));
      throw new Error(`Chunks faltando após upload: ${missing.join(', ')}`);
    }
  }

  private async uploadSingleChunkWithRetry(
    file: File,
    uploadId: string,
    chunkNumber: number,
    controller: AbortController
  ): Promise<void> {
    for (let attempt = 1; attempt <= this.RETRY_ATTEMPTS; attempt++) {
      try {
        await this.uploadSingleChunk(file, uploadId, chunkNumber, controller);
        return; // Sucesso
      } catch (error) {
        if (controller.signal.aborted) {
          throw new Error('Upload cancelado');
        }

        if (attempt === this.RETRY_ATTEMPTS) {
          throw error; // Última tentativa falhou
        }

        // Aguardar antes de tentar novamente (backoff exponencial)
        await this.delay(1000 * attempt);
      }
    }
  }

  private async uploadSingleChunk(
    file: File,
    uploadId: string,
    chunkNumber: number,
    controller: AbortController
  ): Promise<void> {
    const start = (chunkNumber - 1) * this.CHUNK_SIZE;
    const end = Math.min(start + this.CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);

    const formData = new FormData();
    formData.append('chunk', chunk);

    const request = new HttpRequest(
      'POST',
      `${this.chunkedBaseUrl}/${uploadId}/chunk/${chunkNumber}`,
      formData,
      {
        reportProgress: true,
        withCredentials: true
      }
    );

    return new Promise((resolve, reject) => {
      this.http.request(request).subscribe({
        next: (event) => {
          if (event.type === HttpEventType.Response) {
            resolve();
          }
        },
        error: (error) => {
          if (!controller.signal.aborted) {
            reject(error);
          }
        }
      });

      // Cancelamento
      controller.signal.addEventListener('abort', () => {
        reject(new Error('Upload cancelado'));
      });
    });
  }

  private updateProgress(
    progressSubject: BehaviorSubject<UploadProgress>,
    uploadedChunks: number,
    totalChunks: number,
    startTime: number
  ) {
    const now = Date.now();
    const elapsed = (now - startTime) / 1000; // segundos
    const progress = (uploadedChunks / totalChunks) * 100;
    const speed = uploadedChunks > 0 ? (uploadedChunks * this.CHUNK_SIZE) / elapsed : 0;
    const remainingChunks = totalChunks - uploadedChunks;
    const estimatedTimeRemaining = speed > 0 ? (remainingChunks * this.CHUNK_SIZE) / speed : 0;

    progressSubject.next({
      ...progressSubject.value,
      progress,
      speed,
      estimatedTimeRemaining
    });
  }

  private initiateUpload(data: ChunkedUploadInitiate): Observable<ChunkedUploadResponse> {
    return this.http.post<ChunkedUploadResponse>(`${this.chunkedBaseUrl}/initiate`, data, { withCredentials: true });
  }

  private completeUpload(uploadId: string): Observable<ChunkedUploadComplete> {
    return this.http.post<ChunkedUploadComplete>(`${this.chunkedBaseUrl}/${uploadId}/complete`, {}, { withCredentials: true });
  }

  private generateUploadId(): string {
    return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private cleanup(uploadId: string) {
    this.activeUploads.delete(uploadId);
    this.uploadControllers.delete(uploadId);
  }
}
