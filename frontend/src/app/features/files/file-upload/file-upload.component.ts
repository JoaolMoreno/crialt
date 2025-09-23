import { Component, Input, Output, EventEmitter, inject, OnInit, OnDestroy } from '@angular/core';
import { FileService, FileCategory, FileUpload, UploadProgress } from '../../../core/services/file.service';
import { SharedModule } from '../../../shared/shared.module';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [
    SharedModule,
    CommonModule
  ],
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent implements OnInit, OnDestroy {
  @Input() projectId: string | null = null;
  @Input() clientId?: string;
  @Input() stageId?: string;
  @Input() allowedCategories: FileCategory[] = Object.values(FileCategory);
  @Input() multiple = true;
  @Input() maxFileSize = 1 * 1024 * 1024 * 1024;
  @Input() readonly = false;
  @Output() filesChanged = new EventEmitter<FileUpload[]>();

  private readonly fileService = inject(FileService);

  files: FileUpload[] = [];
  dragOver = false;
  error = '';

  editingFile: FileUpload | null = null;
  editFileName: string = '';
  editFileCategory: FileCategory = FileCategory.DOCUMENT;
  FileCategory = FileCategory;

  selectedFiles = new Set<string>();

  activeUploads: UploadProgress[] = [];
  private subscriptions: Subscription[] = [];

  ngOnInit(): void {
    if (this.projectId) {
      this.loadFiles();
    }
    this.activeUploads = this.fileService.getActiveUploads();
  }

  ngOnDestroy() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  get hasActiveUploads(): boolean {
    return this.activeUploads.some(upload =>
      upload.status === 'uploading' || upload.status === 'error'
    );
  }

  get uploading(): boolean {
    return this.hasActiveUploads;
  }

  loadFiles(): void {
    if (!this.projectId) return;

    this.fileService.getFilesByProject(this.projectId).subscribe({
      next: (files) => {
        this.files = files;
        this.selectedFiles.clear();
        this.filesChanged.emit(this.files);
      },
      error: (error) => {
        console.error('Erro ao carregar arquivos:', error);
      }
    });
  }

  onDragOver(event: DragEvent): void {
    if (this.readonly) return;
    event.preventDefault();
    this.dragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    if (this.readonly) return;
    event.preventDefault();
    this.dragOver = false;
  }

  onDrop(event: DragEvent): void {
    if (this.readonly) return;
    event.preventDefault();
    this.dragOver = false;

    const files = Array.from(event.dataTransfer?.files || []);
    this.handleFiles(files);
  }

  onFileSelect(event: Event): void {
    if (this.readonly) return;
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files || []);
    this.handleFiles(files);
    input.value = ''; // Reset input
  }

  private handleFiles(files: File[]): void {
    if (this.readonly) return;

    if (!this.projectId) {
      this.error = 'É necessário salvar o projeto antes de adicionar arquivos.';
      return;
    }

    this.error = '';

    // Validar arquivos
    const validFiles = files.filter(file => {
      if (file.size > this.maxFileSize) {
        this.error = `Arquivo "${file.name}" excede o tamanho máximo de ${this.maxFileSize / 1024 / 1024 / 1024}GB.`;
        return false;
      }
      return true;
    });

    if (validFiles.length === 0) return;

    if (!this.multiple && validFiles.length > 1) {
      this.error = 'Apenas um arquivo é permitido.';
      return;
    }

    // Usar upload chunked para todos os arquivos
    validFiles.forEach(file => this.startChunkedUpload(file));
  }

  private startChunkedUpload(file: File): void {
    const category = this.detectCategory(file);

    const uploadSub = this.fileService.uploadLargeFile(
      file,
      this.projectId!,
      this.clientId,
      this.stageId,
      category
    ).subscribe({
      next: (progress) => {
        this.updateUploadProgress(progress);

        if (progress.status === 'completed') {
          this.handleUploadCompleted(progress);
        }
      },
      error: (error) => {
        console.error('Erro no upload:', error);
        this.error = `Erro no upload do arquivo "${file.name}".`;
      }
    });

    this.subscriptions.push(uploadSub);
  }

  private updateUploadProgress(progress: UploadProgress): void {
    const index = this.activeUploads.findIndex(u => u.uploadId === progress.uploadId);

    if (index >= 0) {
      this.activeUploads[index] = progress;
    } else {
      this.activeUploads.push(progress);
    }

    // Remover uploads completados após um tempo
    if (progress.status === 'completed') {
      setTimeout(() => {
        this.removeUpload(progress.uploadId);
      }, 3000);
    }
  }

  private async handleUploadCompleted(progress: UploadProgress): Promise<void> {
    try {
      // Recarregar lista de arquivos para pegar o novo arquivo
      await this.loadFiles();

      // Verificar se todos os uploads terminaram
      const allCompleted = this.activeUploads.every(u =>
        u.status === 'completed' || u.status === 'error' || u.status === 'cancelled'
      );

      if (allCompleted) {
        // Limpar uploads após todos terminarem
        setTimeout(() => {
          this.activeUploads = this.activeUploads.filter(u =>
            u.status === 'uploading' || u.status === 'error'
          );
        }, 2000);
      }
    } catch (error) {
      console.error('Erro ao buscar arquivo completado:', error);
    }
  }

  cancelUpload(uploadId: string): void {
    this.fileService.cancelUpload(uploadId).subscribe({
      next: () => {
        this.removeUpload(uploadId);
      },
      error: (error) => {
        console.error('Erro ao cancelar upload:', error);
      }
    });
  }

  private removeUpload(uploadId: string): void {
    this.activeUploads = this.activeUploads.filter(u => u.uploadId !== uploadId);
  }

  private detectCategory(file: File): FileCategory {
    const mime = file.type.toLowerCase();
    if (mime.startsWith('image/')) return FileCategory.IMAGE;
    if (mime.startsWith('video/')) return FileCategory.VIDEO;
    return FileCategory.DOCUMENT;
  }

  trackUpload(index: number, upload: UploadProgress): string {
    return upload.uploadId;
  }

  getStatusClass(status: string): string {
    const classes: Record<string, string> = {
      'uploading': 'status-uploading',
      'completed': 'status-completed',
      'error': 'status-error',
      'cancelled': 'status-cancelled'
    };
    return classes[status] || '';
  }

  getStatusText(status: string): string {
    const texts: Record<string, string> = {
      'uploading': 'Enviando...',
      'completed': 'Concluído',
      'error': 'Erro',
      'cancelled': 'Cancelado'
    };
    return texts[status] || status;
  }

  getProgressColor(status: string): 'primary' | 'accent' | 'warn' {
    switch (status) {
      case 'completed': return 'accent';
      case 'error': return 'warn';
      default: return 'primary';
    }
  }

  formatSpeed(bytesPerSecond: number): string {
    const units = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
    let value = bytesPerSecond;
    let unitIndex = 0;

    while (value >= 1024 && unitIndex < units.length - 1) {
      value /= 1024;
      unitIndex++;
    }

    return `${value.toFixed(1)} ${units[unitIndex]}`;
  }

  formatTime(seconds: number): string {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  }

  getOverallProgress(): number {
    if (this.activeUploads.length === 0) return 0;
    const total = this.activeUploads.reduce((sum, upload) => sum + upload.progress, 0);
    return total / this.activeUploads.length;
  }

  getCompletedCount(): number {
    return this.activeUploads.filter(u => u.status === 'completed').length;
  }

  getPendingCount(): number {
    return this.activeUploads.filter(u =>
      u.status === 'uploading' || u.status === 'error'
    ).length;
  }

  downloadFile(file: FileUpload): void {
    this.fileService.downloadFileToDevice(file.id, file.original_name);
  }

  deleteFile(file: FileUpload): void {
    if (this.readonly) return;

    if (!confirm(`Tem certeza que deseja excluir o arquivo "${file.original_name}"?`)) {
      return;
    }

    this.fileService.deleteFile(file.id).subscribe({
      next: () => {
        this.files = this.files.filter(f => f.id !== file.id);
        this.selectedFiles.delete(file.id);
        this.filesChanged.emit(this.files);

        this.error = '';
      },
      error: (error) => {
        console.error('Erro ao excluir arquivo:', error);

        if (error.status === 401 || error.status === 403) {
          this.error = 'Você não tem permissão para excluir este arquivo.';
        } else if (error.status === 404) {
          this.error = 'Arquivo não encontrado.';
          this.files = this.files.filter(f => f.id !== file.id);
          this.selectedFiles.delete(file.id);
          this.filesChanged.emit(this.files);
        } else {
          this.error = 'Erro ao excluir arquivo. Tente novamente.';
        }

        return;
      }
    });
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  getCategoryLabel(category: FileCategory): string {
    const labels: Record<string, string> = {
      [FileCategory.DOCUMENT]: 'Documento',
      [FileCategory.IMAGE]: 'Imagem',
      [FileCategory.VIDEO]: 'Vídeo',
      [FileCategory.PLAN]: 'Planta',
      [FileCategory.RENDER]: 'Render',
      [FileCategory.CONTRACT]: 'Contrato'
    };
    return labels[category] || category;
  }

  getFileIcon(category: FileCategory, mimeType: string): string {
    if (category === FileCategory.IMAGE || mimeType.startsWith('image/')) {
      return 'image';
    }
    if (category === FileCategory.VIDEO || mimeType.startsWith('video/')) {
      return 'movie';
    }
    if (category === FileCategory.PLAN) {
      return 'architecture';
    }
    if (category === FileCategory.RENDER) {
      return 'view_in_ar';
    }
    if (category === FileCategory.CONTRACT) {
      return 'description';
    }
    if (mimeType === 'application/pdf') {
      return 'picture_as_pdf';
    }
    if (mimeType.includes('word') || mimeType.includes('document')) {
      return 'description';
    }
    if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) {
      return 'table_chart';
    }
    return 'insert_drive_file';
  }

  startEditFile(file: FileUpload) {
    if (this.readonly) return;
    this.editingFile = file;
    this.editFileName = file.original_name;
    this.editFileCategory = file.category;
  }

  cancelEditFile() {
    if (this.readonly) return;
    this.editingFile = null;
    this.editFileName = '';
    this.editFileCategory = FileCategory.DOCUMENT;
  }

  saveEditFile() {
    if (this.readonly) return;
    if (!this.editingFile) return;
    const fileId = this.editingFile.id;
    const updated = {
      original_name: this.editFileName,
      category: this.editFileCategory
    };
    this.fileService.updateFile(fileId, updated).subscribe({
      next: (updatedFile: FileUpload) => {
        const idx = this.files.findIndex(f => f.id === fileId);
        if (idx >= 0) this.files[idx] = updatedFile;
        this.editingFile = null;
        this.editFileName = '';
        this.editFileCategory = FileCategory.DOCUMENT;
      },
      error: (err: any) => {
        this.error = 'Erro ao atualizar arquivo.';
      }
    });
  }

  toggleFileSelection(file: FileUpload, checked: boolean) {
    if (checked) {
      this.selectedFiles.add(file.id);
    } else {
      this.selectedFiles.delete(file.id);
    }
  }

  isFileSelected(file: FileUpload): boolean {
    return this.selectedFiles.has(file.id);
  }

  selectAllFiles(checked: boolean) {
    if (checked) {
      this.files.forEach(f => this.selectedFiles.add(f.id));
    } else {
      this.selectedFiles.clear();
    }
  }

  get allFilesSelected(): boolean {
    return this.files.length > 0 && this.selectedFiles.size === this.files.length;
  }

  get anyFileSelected(): boolean {
    return this.selectedFiles.size > 0;
  }

  async downloadSelectedFiles() {
    if (!this.anyFileSelected) return;
    const fileIds = Array.from(this.selectedFiles);
    this.fileService.downloadFilesByIds(fileIds).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'arquivos.zip';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        this.error = 'Erro ao baixar arquivos selecionados.';
      }
    });
  }
}
