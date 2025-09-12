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
  total = 0;
  pageSize = 10;
  currentPage = 1;
  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';
  searchQuery = '';
  selectedCategory = '';
  loading = false;

  ngOnInit(): void {
    this.loadFiles();
  }

  loadFiles(): void {
    this.loading = true;
    const params: Record<string, any> = {
      limit: this.pageSize,
      offset: (this.currentPage - 1) * this.pageSize,
      order_by: this.sortColumn || 'created_at',
      order_dir: this.sortDirection,
      category: this.selectedCategory || undefined,
      search: this.searchQuery || undefined
    };
    this.fileService.getFiles(params).subscribe({
      next: (res) => {
        this.files = res.items;
        this.total = res.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadFiles();
  }

  onSortChange(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.loadFiles();
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadFiles();
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
}
