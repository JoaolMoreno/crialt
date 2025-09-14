import { Component, inject, OnInit } from '@angular/core';
import { ProjectService } from '../../../core/services/project.service';
import { StageTypeService, StageType } from '../../../core/services/stage-type.service';
import { Project } from '../../../core/models/project.model';
import { Stage } from '../../../core/models/stage.model';
import { Router } from '@angular/router';
import { SharedModule } from '../../../shared/shared.module';
import { getStatusBadge } from '../../../core/models/status.model';
import {ProjectCardComponent} from "../project-card/project-card.component";
import { PaginatedProject } from '../../../core/models/paginated-project.model';

@Component({
  selector: 'app-project-list',
  standalone: true,
  templateUrl: './project-list.component.html',
  styleUrls: ['./project-list.component.scss'],
    imports: [SharedModule, ProjectCardComponent]
})
export class ProjectListComponent implements OnInit {
  private readonly projectService = inject(ProjectService);
  private readonly stageTypeService = inject(StageTypeService);
  private readonly router = inject(Router);

  projects: Project[] = [];
  stages: StageType[] = [];
  total = 0;
  pageSize = 10;
  currentPage = 1;
  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';
  searchQuery = '';
  selectedStatus = '';
  selectedPeriod = '';
  selectedStage = '';
  selectedValue = '';
  loading = false;
  error = '';
  selectedProjects: string[] = [];
  batchStatus: string = '';
  viewMode: 'list' | 'grid' = 'list';

  ngOnInit(): void {
    this.loadProjects();
    this.loadStages();
  }

  loadProjects(): void {
    this.loading = true;
    this.error = '';
    const params: Record<string, any> = {
      limit: this.pageSize,
      offset: (this.currentPage - 1) * this.pageSize,
      order_by: this.sortColumn || 'created_at',
      order_dir: this.sortDirection,
      status: this.selectedStatus || undefined,
      stage_type: this.selectedStage || undefined,
      value: this.selectedValue || undefined,
      search: this.searchQuery || undefined,
      period: this.selectedPeriod || undefined
    };
    this.projectService.getProjects(params).subscribe({
      next: (res: PaginatedProject) => {
        this.projects = res.items;
        this.total = res.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Erro ao buscar projetos.';
      }
    });
  }

  loadStages(): void {
    this.stageTypeService.getStageTypes({ is_active: true }).subscribe({
      next: (res) => { this.stages = res.items; },
      error: () => { this.stages = []; }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadProjects();
  }

  onSortChange(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.loadProjects();
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadProjects();
  }

  setViewMode(mode: 'list' | 'grid') {
    this.viewMode = mode;
  }

  getCurrentStage(project: Project): Stage | undefined {
    if (!project.current_stage_id || !project.stages) return undefined;
    return project.stages.find(s => s.id === project.current_stage_id);
  }

  getProjectProgress(project: Project): number {
    if (!project.stages || project.stages.length === 0) return 0;
    const total = project.stages.length;
    const completed = project.stages.filter(s => s.status === 'completed').length;
    return Math.round((completed / total) * 100);
  }

  onEditProject(project: Project): void {
    this.router.navigate(['/projects', project.id, 'edit']);
  }

  onViewProject(project: Project): void {
    this.router.navigate(['/projects', project.id]);
  }

  onNewProject(): void {
    this.router.navigate(['/projects', 'new']);
  }

  onToggleStatus(project: Project): void {
    // Implementar chamada ao serviço para pausar/retomar projeto
  }

  export(format: 'pdf' | 'excel'): void {
    this.loading = true;
    this.projectService.exportProjects(format).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `projetos.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.loading = false;
      },
      error: () => {
        this.error = 'Erro ao exportar projetos.';
        this.loading = false;
      }
    });
  }

  toggleProjectSelection(id: string): void {
    if (this.selectedProjects.includes(id)) {
      this.selectedProjects = this.selectedProjects.filter(pid => pid !== id);
    } else {
      this.selectedProjects.push(id);
    }
  }

  /**
   * Seleciona ou desseleciona todos os projetos da página atual
   */
  toggleSelectAll(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    const pageProjectIds = this.projects.map(p => p.id);
    if (checked) {
      // Adiciona todos os projetos da página atual à seleção, sem duplicar
      this.selectedProjects = Array.from(new Set([...this.selectedProjects, ...pageProjectIds]));
    } else {
      // Remove todos os projetos da página atual da seleção
      this.selectedProjects = this.selectedProjects.filter(id => !pageProjectIds.includes(id));
    }
  }

  updateSelectedProjectsStatus(status: string): void {
    if (this.selectedProjects.length === 0) return;
    this.loading = true;
    this.projectService.updateProjectsStatus(this.selectedProjects, status).subscribe({
      next: () => {
        this.loadProjects();
        this.selectedProjects = [];
        this.loading = false;
      },
      error: () => {
        this.error = 'Erro ao atualizar status dos projetos.';
        this.loading = false;
      }
    });
  }

  statusLabel(status: string): string {
    return getStatusBadge(status).label;
  }
  statusBadgeClass(status: string): string {
    return 'status-badge ' + getStatusBadge(status).color;
  }
  get totalPages(): number {
    return Math.ceil(this.total / this.pageSize);
  }
}
