import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectService } from '../../../core/services/project.service';
import { Project } from '../../../core/models/project.model';
import { Stage } from '../../../core/models/stage.model'; // Removido PaymentStatus
import { ProjectTimelineComponent } from "../project-timeline/project-timeline.component";
import { SharedModule } from "../../../shared/shared.module";
import { ProgressBarComponent } from "../project-progress-bar/progress-bar.component";
import {FileCategory, FileService, FileUpload} from '../../../core/services/file.service';
import { Location } from '@angular/common';
import {getStatusBadge} from "../../../core/models/status.model";

@Component({
  selector: 'app-project-detail',
  standalone: true,
  templateUrl: './project-detail.component.html',
  styleUrls: ['./project-detail.component.scss'],
    imports: [SharedModule, ProgressBarComponent, ProjectTimelineComponent]
})
export class ProjectDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly fileService = inject(FileService);
  private readonly projectService = inject(ProjectService);
  private readonly location = inject(Location);

  projectFiles: FileUpload[] = [];
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
        this.loadProjectFiles(id);
        this.loading = false;
      },
      error: () => {
        this.error = 'Erro ao carregar projeto.';
        this.loading = false;
      }
    });
  }

  loadProjectFiles(projectId: string): void {
    this.fileService.getFilesByProject(projectId).subscribe({
      next: (files) => {
        this.projectFiles = files;
      },
      error: () => {
        this.projectFiles = [];
      }
    });
  }

  getProjectProgress(project: Project): number {
    if (!project.stages || project.stages.length === 0) return 0;
    const totalProgress = project.stages.reduce((sum, stage) => sum + stage.progress_percentage, 0);
    return Math.round(totalProgress / project.stages.length);
  }

  getCurrentStage(project: Project): Stage | null {
    if (!project.current_stage_id || !project.stages) return null;
    // Implementar chamada ao serviço para pausar
    return project.stages.find(s => s.id === project.current_stage_id) || null;
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
    this.location.back();
  }

  statusLabel(status: string): string {
    return getStatusBadge(status).label;
  }
  statusBadgeClass(status: string): string {
    return 'status-badge ' + getStatusBadge(status).color;
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
