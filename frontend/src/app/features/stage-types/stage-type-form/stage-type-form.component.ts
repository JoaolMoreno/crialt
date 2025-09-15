import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { StageTypeService } from '../../../core/services/stage-type.service';
import { ActivatedRoute, Router } from '@angular/router';
import { SharedModule } from '../../../shared/shared.module';
import { StageType } from '../../../core/models/stage-type.model';

@Component({
  selector: 'app-stage-type-form',
  standalone: true,
  templateUrl: './stage-type-form.component.html',
  styleUrls: ['./stage-type-form.component.scss'],
  imports: [SharedModule]
})
export class StageTypeFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly stageTypeService = inject(StageTypeService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  form!: FormGroup;
  loading = false;
  saving = false;
  error = '';
  isEdit = false;
  stageTypeId: string | null = null;
  stageType: StageType | null = null;

  ngOnInit(): void {
    this.stageTypeId = this.route.snapshot.paramMap.get('id');
    this.isEdit = !!this.stageTypeId;

    this.initializeForm();

    if (this.isEdit && this.stageTypeId) {
      this.loadStageType();
    }
  }

  initializeForm(): void {
    this.form = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(100)]],
      description: ['', [Validators.maxLength(500)]],
      is_active: [true]
    });
  }

  loadStageType(): void {
    if (!this.stageTypeId) return;

    this.loading = true;
    this.error = '';

    this.stageTypeService.getStageTypeById(this.stageTypeId).subscribe({
      next: (stageType) => {
        this.stageType = stageType;
        this.form.patchValue({
          name: stageType.name,
          description: stageType.description || '',
          is_active: stageType.is_active
        });
        this.loading = false;
      },
      error: (error) => {
        console.error('Erro ao carregar tipo de etapa:', error);
        this.error = 'Erro ao carregar tipo de etapa. Tente novamente.';
        this.loading = false;
      }
    });
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.markFormGroupTouched();
      return;
    }

    this.saving = true;
    this.error = '';
    const formValue = this.form.value;

    if (this.isEdit && this.stageTypeId) {
      this.stageTypeService.updateStageType(this.stageTypeId, formValue).subscribe({
        next: () => {
          this.router.navigate(['/stages']);
        },
        error: (error) => {
          console.error('Erro ao atualizar tipo de etapa:', error);
          this.error = error.error?.detail || 'Erro ao atualizar tipo de etapa. Tente novamente.';
          this.saving = false;
        }
      });
    } else {
      this.stageTypeService.createStageType(formValue).subscribe({
        next: () => {
          this.router.navigate(['/stages']);
        },
        error: (error) => {
          console.error('Erro ao criar tipo de etapa:', error);
          this.error = error.error?.detail || 'Erro ao criar tipo de etapa. Tente novamente.';
          this.saving = false;
        }
      });
    }
  }

  onCancel(): void {
    this.router.navigate(['/stages']);
  }

  private markFormGroupTouched(): void {
    Object.keys(this.form.controls).forEach(key => {
      const control = this.form.get(key);
      control?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.form.get(fieldName);
    if (field?.errors && field.touched) {
      if (field.errors['required']) {
        return 'Este campo é obrigatório';
      }
      if (field.errors['minlength']) {
        return `Mínimo de ${field.errors['minlength'].requiredLength} caracteres`;
      }
      if (field.errors['maxlength']) {
        return `Máximo de ${field.errors['maxlength'].requiredLength} caracteres`;
      }
    }
    return '';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.form.get(fieldName);
    return !!(field?.invalid && field.touched);
  }
}
