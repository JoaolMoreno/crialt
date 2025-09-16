import { Component, inject, OnInit } from '@angular/core';
import { StageTypeService } from '../../../core/services/stage-type.service';
import { StageType } from '../../../core/models/stage-type.model';
import { Router } from '@angular/router';
import { SharedModule } from '../../../shared/shared.module';
import {StageTypeCardComponent} from "../stage-type-card/stage-type-card.component";
import { Subject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

@Component({
  selector: 'app-stage-type-list',
  standalone: true,
  templateUrl: './stage-type-list.component.html',
  styleUrls: ['./stage-type-list.component.scss'],
  imports: [SharedModule]
})
export class StageTypeListComponent implements OnInit {
  private readonly stageTypeService = inject(StageTypeService);
  private readonly router = inject(Router);

  stageTypes: StageType[] = [];
  total = 0;
  pageSize = 20;
  currentPage = 1;
  sortColumn: string = 'name';
  sortDirection: 'asc' | 'desc' = 'asc';
  searchQuery = '';
  selectedStatus = '';
  loading = false;
  error = '';
  searchLoading = false;
  private searchSubject = new Subject<string>();

  ngOnInit(): void {
    this.searchSubject.pipe(debounceTime(3000)).subscribe((value) => {
      this.searchQuery = value;
      this.currentPage = 1;
      this.searchLoading = false;
      this.loadStageTypes();
    });
    this.loadStageTypes();
  }

  loadStageTypes(): void {
    this.loading = true;
    this.error = '';
    const params: Record<string, any> = {
      limit: this.pageSize,
      offset: (this.currentPage - 1) * this.pageSize,
      order_by: this.sortColumn,
      order_dir: this.sortDirection,
      name: this.searchQuery || undefined,
      is_active: this.selectedStatus === 'active' ? true : this.selectedStatus === 'inactive' ? false : undefined
    };

    this.stageTypeService.getStageTypes(params).subscribe({
      next: (res) => {
        this.stageTypes = res.items;
        this.total = res.total;
        this.loading = false;
      },
      error: (error) => {
        console.error('Erro ao carregar tipos de etapa:', error);
        this.error = 'Erro ao carregar tipos de etapa. Tente novamente.';
        this.loading = false;
      }
    });
  }

  onSort(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.currentPage = 1;
    this.loadStageTypes();
  }

  onSearchInput(value: string): void {
    this.searchLoading = true;
    this.searchSubject.next(value);
  }

  onFilter(): void {
    this.currentPage = 1;
    this.loadStageTypes();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadStageTypes();
  }

  navigateToNew(): void {
    this.router.navigate(['/stages/new']);
  }

  navigateToDetail(id: string): void {
    this.router.navigate(['/stages', id]);
  }

  navigateToEdit(id: string): void {
    this.router.navigate(['/stages', id, 'edit']);
  }

  onDelete(stageType: StageType): void {
    if (confirm(`Tem certeza que deseja excluir o tipo de etapa "${stageType.name}"?`)) {
      this.stageTypeService.deleteStageType(stageType.id).subscribe({
        next: () => {
          this.loadStageTypes();
        },
        error: (error) => {
          console.error('Erro ao excluir tipo de etapa:', error);
          this.error = 'Erro ao excluir tipo de etapa. Tente novamente.';
        }
      });
    }
  }

  getTotalPages(): number {
    return Math.ceil(this.total / this.pageSize);
  }
}
