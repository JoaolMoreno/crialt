import { Component, Input, Output, EventEmitter, inject, OnInit } from '@angular/core';
import { FileService, FileCategory, FileUpload } from '../../../core/services/file.service';
import { SharedModule } from '../../shared.module';
import {MatCheckbox} from "@angular/material/checkbox";


@Component({
  selector: 'app-file-upload',
  standalone: true,
    imports: [SharedModule, MatCheckbox],
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent implements OnInit {
  @Input() projectId: string | null = null;
  @Input() allowedCategories: FileCategory[] = Object.values(FileCategory);
  @Input() multiple = true;
  @Input() maxFileSize = 1 * 1024 * 1024 * 1024;
  @Input() readonly = false;
  @Output() filesChanged = new EventEmitter<FileUpload[]>();

  private readonly fileService = inject(FileService);

  files: FileUpload[] = [];
  uploading = false;
  dragOver = false;
  error = '';

  editingFile: FileUpload | null = null;
  editFileName: string = '';
  editFileCategory: FileCategory = FileCategory.DOCUMENT;
  FileCategory = FileCategory;

  selectedFiles = new Set<string>();

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
    for (const file of files) {
      if (file.size > this.maxFileSize) {
        this.error = `Arquivo "${file.name}" excede o tamanho máximo de ${this.maxFileSize / 1024 / 1024 / 1024}GB.`;
        return;
      }
    }

    if (!this.multiple && files.length > 1) {
      this.error = 'Apenas um arquivo é permitido.';
      return;
    }

    this.uploadFiles(files);
  }

  private detectCategory(file: File): FileCategory {
    const mime = file.type.toLowerCase();
    if (mime.startsWith('image/')) return FileCategory.IMAGE;
    if (mime.startsWith('video/')) return FileCategory.VIDEO;
    return FileCategory.DOCUMENT;
  }

  private uploadFiles(files: File[]): void {
    this.uploading = true;
    let uploadedCount = 0;
    const totalFiles = files.length;

    files.forEach((file) => {
      const category = this.detectCategory(file);
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
