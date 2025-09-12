import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectService } from '../../../core/services/project.service';
import { Project } from '../../../core/models/project.model';
import { Stage } from '../../../core/models/stage.model';
import { getStatusBadge } from '../../../core/models/status.model';
import {SharedModule} from "../../../shared/shared.module";
import {ProgressBarComponent} from "../project-progress-bar/progress-bar.component";

@Component({
  selector: 'app-project-detail',
  standalone: true,
  templateUrl: './project-detail.component.html',
  styleUrls: ['./project-detail.component.scss'],
    imports: [SharedModule, ProgressBarComponent]
})
export class ProjectDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly projectService = inject(ProjectService);

  project: Project | null = null;
  loading = false;
  error = '';
  progress = 0;
  currentStage: Stage | null = null;
  activeTab: 'overview' | 'timeline' | 'files' | 'finance' | 'history' = 'overview';

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) this.loadProject(id);
  }

  loadProject(id: string): void {
    this.loading = true;
    this.projectService.getProjectById(id).subscribe({
      next: (project) => {
        this.project = project;
        this.progress = this.getProjectProgress(project);
        this.currentStage = this.getCurrentStage(project);
        this.loading = false;
      },
      error: () => {
        this.error = 'Erro ao carregar projeto.';
        this.loading = false;
      }
    });
  }

  getProjectProgress(project: Project): number {
    if (!project.stages || project.stages.length === 0) return 0;
    const total = project.stages.length;
    const completed = project.stages.filter(s => s.status === 'completed').length;
    return Math.round((completed / total) * 100);
  }

  getCurrentStage(project: Project): Stage | null {
    return project.stages.find(s => s.status === 'in_progress') || null;
  }

  setTab(tab: 'overview' | 'timeline' | 'files' | 'finance' | 'history') {
    this.activeTab = tab;
  }

  onEditProject() {
    if (this.project) this.router.navigate(['/projects', this.project.id, 'edit']);
  }
  onPauseProject() {
    // Implementar chamada ao serviço para pausar
  }
  onFinishProject() {
    // Implementar chamada ao serviço para finalizar
  }
  onBack(): void {
    this.router.navigate(['/projects']);
  }

  statusLabel(status: string): string {
    return getStatusBadge(status).label;
  }
  statusBadgeClass(status: string): string {
    return 'status-badge ' + getStatusBadge(status).color;
  }

    protected readonly String = String;
    protected readonly Number = Number;
    protected readonly Boolean = Boolean;
    protected readonly Object = Object;
    protected readonly Array = Array;
}
