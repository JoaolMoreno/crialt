import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ProjectService } from '../../../core/services/project.service';
import { Project } from '../../../core/models/project.model';
import { Stage } from '../../../core/models/stage.model';
import {DatePipe, NgClass, NgForOf, NgIf} from "@angular/common";
import {LoadingSpinnerComponent} from "../../../shared/components/loading-spinner/loading-spinner.component";
import { getStatusBadge } from '../../../core/models/status.model';

@Component({
    selector: 'app-project-timeline',
    standalone: true,
    templateUrl: './project-timeline.component.html',
    imports: [
        DatePipe,
        LoadingSpinnerComponent,
        NgIf,
        NgForOf,
        NgClass
    ],
    styleUrls: ['./project-timeline.component.scss']
})
export class ProjectTimelineComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly projectService = inject(ProjectService);

  project: Project | null = null;
  stages: Stage[] = [];
  loading = false;
  error = '';

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) this.loadProject(id);
  }

  loadProject(id: string): void {
    this.loading = true;
    this.projectService.getProjectById(id).subscribe({
      next: (project) => {
        this.project = project;
        this.stages = project.stages || [];
        this.loading = false;
      },
      error: () => {
        this.error = 'Erro ao carregar timeline do projeto.';
        this.loading = false;
      }
    });
  }

  viewStageDetail(stage: Stage): void {
    // Exemplo: navegar para detalhes da etapa
    // this.router.navigate(['/stages', stage.id]);
    // Ou abrir modal de detalhes
    alert(`Detalhes da etapa: ${stage.name}`);
  }

  exportTimeline(format: 'pdf' | 'image'): void {
    this.loading = true;
    // Exemplo: usar o serviço para exportar timeline
    this.projectService.getProjectTimeline(this.project?.id || '').subscribe({
      next: (timelineData) => {
        // Simulação de exportação
        alert(`Exportação da timeline em formato ${format} não implementada.`);
        this.loading = false;
      },
      error: () => {
        this.error = 'Erro ao exportar timeline.';
        this.loading = false;
      }
    });
  }

  filterByPeriod(period: string): void {
    if (!period) {
      this.stages = this.project?.stages || [];
      return;
    }
    this.stages = (this.project?.stages || []).filter(stage => {
      const start = stage.actual_start_date || stage.planned_start_date;
      return start && start.startsWith(period);
    });
  }

  onPeriodChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.filterByPeriod(value);
  }

  statusLabel(status: string): string {
    return getStatusBadge(status).label;
  }
  statusBadgeClass(status: string): string {
    return 'status-badge ' + getStatusBadge(status).color;
  }
}
