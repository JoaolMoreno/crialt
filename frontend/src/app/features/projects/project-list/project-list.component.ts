import { Component, inject, OnInit } from '@angular/core';
import { ProjectService } from '../../../core/services/project.service';
import { ClientService } from '../../../core/services/client.service';
import { StageService } from '../../../core/services/stage.service';
import { Project } from '../../../core/models/project.model';
import { Client } from '../../../core/models/client.model';
import { Stage } from '../../../core/models/stage.model';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { FormsModule } from '@angular/forms';
import {CurrencyPipe, DatePipe, NgClass, NgForOf, NgIf} from '@angular/common';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';
import {ProjectCardComponent} from "../project-card/project-card.component";

@Component({
  selector: 'app-project-list',
  standalone: true,
  templateUrl: './project-list.component.html',
  styleUrls: ['./project-list.component.scss'],
    imports: [FormsModule, DatePipe, LoadingSpinnerComponent, NgIf, NgForOf, CurrencyPipe, ProjectCardComponent, NgClass]
})
export class ProjectListComponent implements OnInit {
  private readonly projectService = inject(ProjectService);
  private readonly clientService = inject(ClientService);
  private readonly stageService = inject(StageService);
  private readonly router = inject(Router);
  private readonly authService = inject(AuthService);

  projects: Project[] = [];
  filteredProjects: Project[] = [];
  paginatedProjects: Project[] = [];
  clients: Client[] = [];
  stages: Stage[] = [];
  loading = false;
  error = '';
  searchQuery = '';
  selectedStatus = '';
  selectedClient = '';
  selectedPeriod = '';
  selectedStage = '';
  selectedValue = '';
  isAdmin = false;
  selectedProjects: string[] = [];
  batchStatus: string = '';

  // Paginação
  pageSize = 10;
  currentPage = 1;
  totalPages = 1;
  // Ordenação
  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';
  viewMode: 'list' | 'grid' = 'list';

  ngOnInit(): void {
    this.authService.getCurrentUser().subscribe(user => {
      this.isAdmin = user?.role === 'admin';
    });
    this.loadProjects();
    this.loadClientsAndStages();
  }

  loadProjects(): void {
    this.loading = true;
    this.error = '';
    this.projectService.getProjects().subscribe({
      next: (projects) => {
        this.projects = projects;
        this.filteredProjects = projects;
        this.totalPages = Math.ceil(projects.length / this.pageSize) || 1;
        this.currentPage = 1;
        this.paginate();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Erro ao carregar projetos.';
        this.loading = false;
      }
    });
  }

  loadClientsAndStages(): void {
    this.clientService.getClients().subscribe({
      next: (clients) => { this.clients = clients; },
      error: () => { this.clients = []; }
    });
    this.stageService.getStages().subscribe({
      next: (stages) => { this.stages = stages; },
      error: () => { this.stages = []; }
    });
  }

  applyFilters(): void {
    let filtered = [...this.projects];
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(query) ||
        (p.clients[0]?.name?.toLowerCase().includes(query)) ||
        (this.getCurrentStage(p)?.name?.toLowerCase().includes(query))
      );
    }
    if (this.selectedStatus) {
      filtered = filtered.filter(p => p.status === this.selectedStatus);
    }
    if (this.selectedClient) {
      filtered = filtered.filter(p => p.clients.some(c => c.id === this.selectedClient));
    }
    if (this.selectedStage) {
      filtered = filtered.filter(p => p.stages.some(s => s.id === this.selectedStage));
    }
    if (this.selectedPeriod) {
      filtered = filtered.filter(p => p.created_at?.startsWith(this.selectedPeriod));
    }
    if (this.selectedValue) {
      filtered = filtered.filter(p => p.total_value >= +this.selectedValue);
    }
    this.filteredProjects = filtered;
    this.totalPages = Math.ceil(filtered.length / this.pageSize) || 1;
    this.currentPage = 1;
    this.paginate();
  }

  setViewMode(mode: 'list' | 'grid') {
    this.viewMode = mode;
  }

  getCurrentStage(project: Project): Stage | undefined {
    return project.stages.find(s => s.status === 'in_progress');
  }

  getProjectProgress(project: Project): number {
    if (!project.stages || project.stages.length === 0) return 0;
    const total = project.stages.length;
    const completed = project.stages.filter(s => s.status === 'completed').length;
    return Math.round((completed / total) * 100);
  }

  paginate(): void {
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    this.paginatedProjects = this.filteredProjects.slice(start, end);
  }

  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages) return;
    this.currentPage = page;
    this.paginate();
  }

  sortBy(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.filteredProjects.sort((a, b) => {
      let aValue: any = '';
      let bValue: any = '';
      switch (column) {
        case 'name':
          aValue = a.name;
          bValue = b.name;
          break;
        case 'client':
          aValue = a.clients[0]?.name || '';
          bValue = b.clients[0]?.name || '';
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'stage':
          aValue = this.getCurrentStage(a)?.name || '';
          bValue = this.getCurrentStage(b)?.name || '';
          break;
        case 'value':
          aValue = a.total_value;
          bValue = b.total_value;
          break;
        case 'created_at':
          aValue = a.created_at;
          bValue = b.created_at;
          break;
      }
      if (aValue < bValue) return this.sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return this.sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
    this.paginate();
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
    const pageProjectIds = this.paginatedProjects.map(p => p.id);
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
    switch (status) {
      case 'draft': return 'Rascunho';
      case 'active': return 'Ativo';
      case 'paused': return 'Pausado';
      case 'completed': return 'Concluído';
      case 'cancelled': return 'Cancelado';
      case 'in_progress': return 'Em andamento';
      default: return status;
    }
  }

  statusBadgeClass(status: string | undefined): string {
    switch (status) {
      case 'draft': return 'badge-draft';
      case 'active': return 'badge-active';
      case 'paused': return 'badge-paused';
      case 'completed': return 'badge-completed';
      case 'cancelled': return 'badge-cancelled';
      case 'in_progress': return 'badge-active';
      default: return 'badge-draft';
    }
  }
}
