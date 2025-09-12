import { Component, inject, OnInit } from '@angular/core';
import { FileService } from '../../../core/services/file.service';
import { File } from '../../../core/models/file.model';
import { SharedModule } from '../../../shared/shared.module';

@Component({
  selector: 'app-file-list',
  standalone: true,
  templateUrl: './file-list.component.html',
  styleUrls: ['./file-list.component.scss'],
    imports: [SharedModule]
})
export class FileListComponent implements OnInit {
  private readonly fileService = inject(FileService);

  files: File[] = [];
  filteredFiles: File[] = [];
  loading = false;
  searchQuery = '';
  selectedCategory = '';

  ngOnInit(): void {
    this.loadFiles();
  }

  loadFiles(): void {
    this.loading = true;
    this.fileService.getFiles().subscribe({
      next: (files) => {
        this.files = files;
        this.applyFilters();
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    this.filteredFiles = this.files.filter(file => {
      const matchesCategory = this.selectedCategory ? file.category === this.selectedCategory : true;
      const matchesSearch = this.searchQuery ? file.original_name.toLowerCase().includes(this.searchQuery.toLowerCase()) : true;
      return matchesCategory && matchesSearch;
    });
  }

  onOpenUploadModal(): void {
    // Abrir modal de upload (a implementar)
  }

  onDownload(file: File): void {
    window.open(`/api/files/${file.id}/download`, '_blank');
  }

  onDelete(file: File): void {
    if (confirm(`Deseja realmente excluir o arquivo "${file.original_name}"?`)) {
      this.loading = true;
      this.fileService.deleteFile(file.id).subscribe({
        next: () => {
          this.loadFiles();
        },
        error: () => {
          this.loading = false;
        }
      });
    }
  }

  // Atualiza filtros ao mudar busca ou categoria
  ngOnChanges(): void {
    this.applyFilters();
  }
}
