import { Component, inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ProjectService } from '../../../core/services/project.service';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';

@Component({
    selector: 'app-project-form',
    standalone: true,
    templateUrl: './project-form.component.html',
    imports: [
        ReactiveFormsModule
    ],
    styleUrls: ['./project-form.component.scss']
})
export class ProjectFormComponent {
  isEdit = false;
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly projectService = inject(ProjectService);
  private readonly fb = inject(FormBuilder);

  form: FormGroup;
  loading = false;
  error = '';
  projectId: string | null = null;

  constructor() {
    const id = this.route.snapshot.paramMap.get('id');
    this.isEdit = !!id;
    this.projectId = id;
    this.form = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      clientId: ['', Validators.required],
      value: ['', Validators.required],
      startDate: ['', Validators.required],
      endDate: ['', Validators.required],
      address: [''],
      // Adicione outros campos conforme necessário
    });
    if (this.isEdit && id) {
      this.loadProject(id);
    }
  }

  loadProject(id: string): void {
    this.loading = true;
    this.projectService.getProjectById(id).subscribe({
      next: (project) => {
        this.form.patchValue(project);
        this.loading = false;
      },
      error: () => {
        this.error = 'Erro ao carregar projeto.';
        this.loading = false;
      }
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    const data = this.form.value;
    if (this.isEdit && this.projectId) {
      this.projectService.updateProject(this.projectId, data).subscribe({
        next: () => {
          this.router.navigate(['/projects']);
        },
        error: () => {
          this.error = 'Erro ao atualizar projeto.';
          this.loading = false;
        }
      });
    } else {
      this.projectService.createProject(data).subscribe({
        next: () => {
          this.router.navigate(['/projects']);
        },
        error: () => {
          this.error = 'Erro ao criar projeto.';
          this.loading = false;
        }
      });
    }
  }

  onBack(): void {
    this.router.navigate(['/projects']);
  }
}
