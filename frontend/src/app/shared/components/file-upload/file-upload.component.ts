import { Component, Input, Output, EventEmitter, inject, OnInit } from '@angular/core';
import { FileService, FileCategory, FileUpload } from '../../../core/services/file.service';
import { SharedModule } from '../../shared.module';


@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [SharedModule],
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent implements OnInit {
  @Input() projectId: string | null = null;
  @Input() allowedCategories: FileCategory[] = Object.values(FileCategory);
  @Input() multiple = true;
  @Input() maxFileSize = 10 * 1024 * 1024; // 10MB
  @Output() filesChanged = new EventEmitter<FileUpload[]>();

  private readonly fileService = inject(FileService);

  files: FileUpload[] = [];
  uploading = false;
  dragOver = false;
  error = '';

  ngOnInit(): void {
    if (this.projectId) {
      this.loadFiles();
    }
  }

  loadFiles(): void {
    if (!this.projectId) return;

    this.fileService.getFilesByProject(this.projectId).subscribe({
      next: (files) => {
        this.files = files;
        this.filesChanged.emit(this.files);
      },
      error: (error) => {
        console.error('Erro ao carregar arquivos:', error);
      }
    });
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = false;

    const files = Array.from(event.dataTransfer?.files || []);
    this.handleFiles(files);
  }

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files || []);
    this.handleFiles(files);
    input.value = ''; // Reset input
  }

  private handleFiles(files: File[]): void {
    if (!this.projectId) {
      this.error = 'É necessário salvar o projeto antes de adicionar arquivos.';
      return;
    }

    this.error = '';

    // Validar arquivos
    for (const file of files) {
      if (file.size > this.maxFileSize) {
        this.error = `Arquivo "${file.name}" excede o tamanho máximo de ${this.maxFileSize / 1024 / 1024}MB.`;
        return;
      }
    }

    if (!this.multiple && files.length > 1) {
      this.error = 'Apenas um arquivo é permitido.';
      return;
    }

    // Upload dos arquivos
    this.uploadFiles(files);
  }

  private uploadFiles(files: File[]): void {
    this.uploading = true;
    let uploadedCount = 0;
    const totalFiles = files.length;

    files.forEach((file) => {
      // Por padrão, usamos 'document' como categoria. No futuro, pode ser customizado
      const category = this.getDefaultCategory(file);

      this.fileService.uploadFile(file, this.projectId!, category).subscribe({
        next: (uploadedFile) => {
          this.files.push(uploadedFile);
          uploadedCount++;

          if (uploadedCount === totalFiles) {
            this.uploading = false;
            this.filesChanged.emit(this.files);
          }
        },
        error: (error) => {
          console.error('Erro ao fazer upload:', error);
          this.error = `Erro ao fazer upload do arquivo "${file.name}".`;
          uploadedCount++;

          if (uploadedCount === totalFiles) {
            this.uploading = false;
          }
        }
      });
    });
  }

  private getDefaultCategory(file: File): FileCategory {
    const mimeType = file.type.toLowerCase();
    const extension = file.name.split('.').pop()?.toLowerCase() || '';

    if (mimeType.startsWith('image/') || ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) {
      return FileCategory.IMAGE;
    }

    if (['dwg', 'dxf', 'pdf'].includes(extension)) {
      return FileCategory.PLAN;
    }

    if (['pdf'].includes(extension) && file.name.toLowerCase().includes('contrato')) {
      return FileCategory.CONTRACT;
    }

    return FileCategory.DOCUMENT;
  }

  downloadFile(file: FileUpload): void {
    this.fileService.downloadFileToDevice(file.id, file.original_name);
  }

  deleteFile(file: FileUpload): void {
    if (!confirm(`Tem certeza que deseja excluir o arquivo "${file.original_name}"?`)) {
      return;
    }

    this.fileService.deleteFile(file.id).subscribe({
      next: () => {
        this.files = this.files.filter(f => f.id !== file.id);
        this.filesChanged.emit(this.files);
      },
      error: (error) => {
        console.error('Erro ao excluir arquivo:', error);
        this.error = 'Erro ao excluir arquivo.';
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
    const labels = {
      [FileCategory.DOCUMENT]: 'Documento',
      [FileCategory.IMAGE]: 'Imagem',
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
}
