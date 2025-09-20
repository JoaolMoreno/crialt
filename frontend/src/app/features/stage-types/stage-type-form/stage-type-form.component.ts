import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { StageTypeService } from '../../../core/services/stage-type.service';
import { ActivatedRoute, Router } from '@angular/router';
import { SharedModule } from '../../../shared/shared.module';
import { StageType } from '../../../core/models/stage-type.model';
import { NotificationService } from '../../../shared/notification.service';

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
  private readonly notification = inject(NotificationService);

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
        this.form.patchValue(stageType);
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Erro ao carregar tipo de etapa.';
        this.notification.error(err);
        this.loading = false;
      }
    });
  }

  saveStageType(): void {
    if (this.form.invalid) {
      this.notification.error('Formulário inválido.');
      return;
    }

    this.saving = true;
    const data = this.form.value;

    if (this.isEdit && this.stageTypeId) {
      this.stageTypeService.updateStageType(this.stageTypeId, data).subscribe({
        next: () => {
          this.notification.success('Tipo de etapa atualizado com sucesso!');
          this.router.navigate(['/stage-types']);
        },
        error: (err) => {
          this.notification.error(err);
          this.saving = false;
        }
      });
    } else {
      this.stageTypeService.createStageType(data).subscribe({
        next: () => {
          this.notification.success('Tipo de etapa criado com sucesso!');
          this.router.navigate(['/stage-types']);
        },
        error: (err) => {
          this.notification.error(err);
          this.saving = false;
        }
      });
    }
  }

  onSubmit(): void {
    this.saveStageType();
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
