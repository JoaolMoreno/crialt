import { Component, Input } from '@angular/core';
import { Stage } from '../../../core/models/stage.model';
import { getStatusBadge } from '../../../core/models/status.model';
import { SharedModule } from '../../../shared/shared.module';

@Component({
  selector: 'app-project-timeline',
  standalone: true,
  imports: [SharedModule],
  templateUrl: './project-timeline.component.html',
  styleUrls: ['./project-timeline.component.scss']
})
export class ProjectTimelineComponent {
  @Input() projectId!: string;
  @Input() stages: Stage[] = [];

  selectedStage: Stage | null = null;
  selectedStageIndex: number = 0;

  statusLabel(status: string): string {
    return getStatusBadge(status).label;
  }

  statusBadgeClass(status: string): string {
    return 'status-badge ' + getStatusBadge(status).color;
  }

  getSortedStages(): Stage[] {
    return [...this.stages].sort((a, b) => a.order - b.order);
  }

  trackByStageId(index: number, stage: Stage): string {
    return stage.id;
  }

  openStageCard(stage: Stage, index: number): void {
    this.selectedStage = stage;
    this.selectedStageIndex = index;
  }

  closeStageCard(): void {
    this.selectedStage = null;
    this.selectedStageIndex = 0;
  }
}
