import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Project } from '../../../core/models/project.model';
import { ProgressBarComponent } from '../../projects/project-progress-bar/progress-bar.component';

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

    get activeStageName(): string {
        if (!this.project?.stages?.length) return '-';
        const activeStage = this.project.stages.find(s => s.status === 'in_progress');
        return activeStage?.name || '-';
    }
}
