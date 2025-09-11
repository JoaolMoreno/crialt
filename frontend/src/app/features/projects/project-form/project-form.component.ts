import { Component, inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ProjectService } from '../../../core/services/project.service';
import {FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors} from '@angular/forms';
import { ClientService } from '../../../core/services/client.service';
import { Client } from '../../../core/models/client.model';
import { NgIf, NgForOf } from '@angular/common';
import { StageService } from '../../../core/services/stage.service';
import { Stage } from '../../../core/models/stage.model';

@Component({
    selector: 'app-project-form',
    standalone: true,
    templateUrl: './project-form.component.html',
    imports: [
        ReactiveFormsModule,
        NgIf,
        NgForOf,
        FormsModule
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

  clients: Client[] = [];
  selectedClients: Client[] = [];
  showClientModal = false;
  clientSearch = '';
  loadingClients = false;

  stages: Stage[] = [];
  selectedStages: Stage[] = [];
  showStageModal = false;
  stageSearch = '';
  loadingStages = false;

  private readonly clientService = inject(ClientService);
  private readonly stageService = inject(StageService);

  constructor() {
    const id = this.route.snapshot.paramMap.get('id');
    this.isEdit = !!id;
    this.projectId = id;
    this.form = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      clientId: [[], Validators.required],
      stages: [[], []],
      value: ['', [Validators.required, moedaBrValidator]],
      startDate: ['', Validators.required],
      endDate: ['', Validators.required],
      address: [''],
      scope: [''],
    });
    if (this.isEdit && id) {
      this.loadProject(id);
    }
    this.loadClients();
    this.loadStages();
  }

  loadClients(): void {
    this.loadingClients = true;
    this.clientService.getClients().subscribe({
      next: (clients) => {
        this.clients = clients;
        this.loadingClients = false;
      },
      error: () => {
        this.loadingClients = false;
      }
    });
  }

  openClientModal(): void {
    this.showClientModal = true;
    this.clientSearch = '';
  }

  closeClientModal(): void {
    this.showClientModal = false;
  }

  get filteredClients(): Client[] {
    if (!this.clientSearch) return this.clients;
    const search = this.clientSearch.toLowerCase();
    return this.clients.filter(c =>
      c.name.toLowerCase().includes(search) ||
      c.document.toLowerCase().includes(search)
    );
  }

  toggleClientSelection(client: Client): void {
    const idx = this.selectedClients.findIndex(c => c.id === client.id);
    if (idx >= 0) {
      this.selectedClients.splice(idx, 1);
    } else {
      this.selectedClients.push(client);
    }
    this.form.get('clientId')?.setValue(this.selectedClients.map(c => c.id));
    this.form.get('clientId')?.markAsDirty();
  }

  isClientSelected(client: Client): boolean {
    return this.selectedClients.some(c => c.id === client.id);
  }

  loadStages(): void {
    this.loadingStages = true;
    this.stageService.getStages().subscribe({
      next: (stages) => {
        this.stages = stages;
        this.loadingStages = false;
      },
      error: () => {
        this.loadingStages = false;
      }
    });
  }

  openStageModal(): void {
    this.showStageModal = true;
    this.stageSearch = '';
  }

  closeStageModal(): void {
    this.showStageModal = false;
  }

  get filteredStages(): Stage[] {
    if (!this.stageSearch) return this.stages;
    const search = this.stageSearch.toLowerCase();
    return this.stages.filter(s =>
      s.name.toLowerCase().includes(search)
    );
  }

  toggleStageSelection(stage: Stage): void {
    const idx = this.selectedStages.findIndex(s => s.id === stage.id);
    if (idx >= 0) {
      this.selectedStages.splice(idx, 1);
    } else {
      this.selectedStages.push(stage);
    }
    this.form.get('stages')?.setValue(this.selectedStages.map(s => s.id));
    this.form.get('stages')?.markAsDirty();
  }

  isStageSelected(stage: Stage): boolean {
    return this.selectedStages.some(s => s.id === stage.id);
  }

  loadProject(id: string): void {
    this.loading = true;
    this.projectService.getProjectById(id).subscribe({
      next: (project) => {
        this.form.patchValue({
          ...project,
          clientId: project.clients.map(c => c.id),
          stages: project.stages.map(s => s.id)
        });
        this.selectedClients = project.clients;
        this.selectedStages = project.stages;
        this.loading = false;
      },
      error: () => {
        this.error = 'Erro ao carregar projeto.';
        this.loading = false;
      }
    });
  }

  formatValueInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    let value = input.value.replace(/\D/g, '');
    // Remove zeros à esquerda, mas mantém pelo menos um zero
    value = value.replace(/^0+/, '');
    if (!value) {
      input.value = '';
      this.form.get('value')?.setValue('');
      return;
    }
    // Garante pelo menos 3 dígitos para 0,01
    while (value.length < 3) value = '0' + value;
    const intPart = value.slice(0, value.length - 2);
    const decPart = value.slice(-2);
    // Adiciona separador de milhar
    const intFormatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    input.value = `${intFormatted},${decPart}`;
    this.form.get('value')?.setValue(input.value);
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    const formValue = this.form.value;
    const data: any = {
      name: formValue.name,
      description: formValue.description,
      total_value: moedaBrToFloat(formValue.value),
      start_date: formValue.startDate,
      estimated_end_date: formValue.endDate,
      clients: this.selectedClients.map(c => c.id),
      stages: this.selectedStages.map(s => s.id),
      address: typeof formValue.address === 'string' ? { street: formValue.address } : formValue.address,
      scope: typeof formValue.scope === 'string' ? { technical_notes: formValue.scope } : formValue.scope,
    };
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

function moedaBrValidator(control: AbstractControl): ValidationErrors | null {
  const value = control.value;
  if (!value) {
    return { required: true };
  }
  // Aceita apenas valores positivos, formato correto e maior que zero
  const regex = /^(0,[1-9]\d|0,0[1-9]|[1-9]\d{0,2}(\.\d{3})*,\d{2}|[1-9]\d*,\d{2})$/;
  const regexTest = regex.test(value);
  if (!regexTest) {
    return { moedaBr: true };
  }
  const floatValue = moedaBrToFloat(value);
  if (floatValue <= 0) {
    return { moedaBr: true };
  }
  return null;
}

function moedaBrToFloat(valor: string): number {
  if (!valor) return 0;
  return parseFloat(valor.replace(/\./g, '').replace(',', '.'));
}
