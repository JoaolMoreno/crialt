import { Component, inject, OnInit } from '@angular/core';
import { StageTypeService } from '../../../core/services/stage-type.service';
import { ActivatedRoute, Router } from '@angular/router';
import { SharedModule } from '../../../shared/shared.module';
import { StageType } from '../../../core/models/stage-type.model';

@Component({
  selector: 'app-stage-type-detail',
  standalone: true,
  templateUrl: './stage-type-detail.component.html',
  styleUrls: ['./stage-type-detail.component.scss'],
  imports: [SharedModule]
})
export class StageTypeDetailComponent implements OnInit {
  private readonly stageTypeService = inject(StageTypeService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  stageType: StageType | null = null;
  loading = false;
  error = '';
  stageTypeId: string | null = null;

  ngOnInit(): void {
    this.stageTypeId = this.route.snapshot.paramMap.get('id');
    if (this.stageTypeId) {
      this.loadStageType();
    }
  }

  loadStageType(): void {
    if (!this.stageTypeId) return;

    this.loading = true;
    this.error = '';

    this.stageTypeService.getStageTypeById(this.stageTypeId).subscribe({
      next: (stageType) => {
        this.stageType = stageType;
        this.loading = false;
      },
      error: (error) => {
        console.error('Erro ao carregar tipo de etapa:', error);
        this.error = 'Erro ao carregar tipo de etapa. Tente novamente.';
        this.loading = false;
      }
    });
  }

  navigateToEdit(): void {
    if (this.stageTypeId) {
      this.router.navigate(['/stages', this.stageTypeId, 'edit']);
    }
  }

  navigateToList(): void {
    this.router.navigate(['/stages']);
  }

  onDelete(): void {
    if (!this.stageType) return;

    if (confirm(`Tem certeza que deseja excluir o tipo de etapa "${this.stageType.name}"?`)) {
      this.stageTypeService.deleteStageType(this.stageType.id).subscribe({
        next: () => {
          this.router.navigate(['/stages']);
        },
        error: (error) => {
          console.error('Erro ao excluir tipo de etapa:', error);
          this.error = 'Erro ao excluir tipo de etapa. Tente novamente.';
        }
      });
    }
  }
}
