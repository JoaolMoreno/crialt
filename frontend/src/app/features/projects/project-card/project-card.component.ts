import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Project } from '../../../core/models/project.model';
import { ProgressBarComponent } from '../project-progress-bar/progress-bar.component';
import { getStatusBadge } from '../../../core/models/status.model';

@Component({
    selector: 'app-project-card',
    templateUrl: './project-card.component.html',
    styleUrls: ['./project-card.component.scss'],
    standalone: true,
    imports: [CommonModule, ProgressBarComponent]
})
export class ProjectCardComponent {
    @Input() project!: Project;
    @Input() progress: number = 0;
    @Output() edit = new EventEmitter<Project>();
    @Output() view = new EventEmitter<Project>();

    get activeStageName(): string {
        if (!this.project?.stages?.length) return '-';
        const activeStage = this.project.stages.find(s => s.status === 'in_progress');
        return activeStage?.name || '-';
    }
    statusLabel(status: string): string {
        return getStatusBadge(status).label;
    }
    statusBadgeClass(status: string): string {
        return 'status-badge ' + getStatusBadge(status).color;
    }
    onEdit() {
        this.edit.emit(this.project);
    }
    onView() {
        this.view.emit(this.project);
    }
}
