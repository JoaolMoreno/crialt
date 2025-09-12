import { Component, inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ProjectService } from '../../../core/services/project.service';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { ClientService } from '../../../core/services/client.service';
import { Client } from '../../../core/models/client.model';
import { StageService } from '../../../core/services/stage.service';
import { Stage } from '../../../core/models/stage.model';
import { getStatusBadge } from '../../../core/models/status.model';
import { SharedModule } from "../../../shared/shared.module";

@Component({
    selector: 'app-project-form',
    standalone: true,
    templateUrl: './project-form.component.html',
    imports: [SharedModule],
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

  etapasDisponiveis: Stage[] = [];
  etapasProjeto: Stage[] = [];
  showEtapaModal = false;
  etapaSearch = '';
  etapasSelecionadas: Stage[] = [];

  private readonly clientService = inject(ClientService);
  private readonly stageService = inject(StageService);

  etapasVisuais: { id: string; active: boolean; expanded: boolean }[] = [];

  editProjectStatus = false;
  projectStatus: string = 'draft';
  editStageStatus: { [id: string]: boolean } = {};

  constructor() {
    const id = this.route.snapshot.paramMap.get('id');
    this.isEdit = !!id;
    this.projectId = id;
    this.form = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      value: [0, Validators.required],
      startDate: ['', Validators.required],
      endDate: ['', Validators.required],
      address: [''],
      scope: this.fb.group({
        total_area: [''],
        rooms_included: [''],
        technical_notes: ['']
      }),
      clientId: [[], Validators.required],
      stages: [[], []],
      status: ['draft', Validators.required],
    });
    if (this.isEdit && id) {
      this.loadProject(id);
    }
    this.loadClients();
    this.loadStages();
  }

  ngOnInit(): void {
    // Se o status estiver no form, inicializa
    if (this.form.get('status')) {
      this.projectStatus = this.form.get('status')?.value || 'draft';
    }
  }

  toggleEditProjectStatus(): void {
    this.editProjectStatus = !this.editProjectStatus;
    if (!this.editProjectStatus) {
      // Cancela edição, restaura valor do form
      this.form.get('status')?.setValue(this.projectStatus);
    }
  }

  saveProjectStatus(): void {
    this.projectStatus = this.form.get('status')?.value;
    this.editProjectStatus = false;
  }

  toggleEditStageStatus(id: string): void {
    this.editStageStatus[id] = !this.editStageStatus[id];
    if (!this.editStageStatus[id]) {
      // Cancela edição, restaura valor original se necessário
      // (opcional, depende se quer manter alteração ou não)
    }
  }

  saveStageStatus(id: string): void {
    this.editStageStatus[id] = false;
    // O status já está alterado no objeto stage
  }

  loadClients(): void {
    this.loadingClients = true;
    this.clientService.getClients().subscribe({
      next: (clients) => {
        this.clients = clients.items;
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

  loadingStages = false;
  loadStages(): void {
    this.loadingStages = true;
    this.stageService.getStages().subscribe({
      next: (stages) => {
        this.etapasDisponiveis = stages.items;
        this.loadingStages = false;
      },
      error: () => {
        this.loadingStages = false;
      }
    });
  }

  openEtapaModal(): void {
    this.showEtapaModal = true;
    this.etapaSearch = '';
    this.etapasSelecionadas = [];
  }

  closeEtapaModal(): void {
    this.showEtapaModal = false;
  }

  removerEtapa(id: string) {
    this.etapasProjeto = this.etapasProjeto.filter(e => e.id !== id);
    this.etapasVisuais = this.etapasVisuais.filter(e => e.id !== id);
  }

  getVisual(id: string) {
    return this.etapasVisuais.find(e => e.id === id);
  }

  toggleEtapaActive(id: string) {
    const visual = this.getVisual(id);
    if (visual) visual.active = !visual.active;
  }

  toggleEtapaExpanded(id: string) {
    const visual = this.getVisual(id);
    if (visual) visual.expanded = !visual.expanded;
  }

  etapasAtivas(): Stage[] {
    return this.etapasProjeto.filter(stage => this.getVisual(stage.id)?.active);
  }

  loadProject(id: string): void {
    this.loading = true;
    this.projectService.getProjectById(id).subscribe({
      next: (project) => {
        this.form.patchValue({
          name: project.name,
          description: project.description,
          value: project.total_value,
          startDate: project.start_date,
          endDate: project.estimated_end_date,
          address: project.work_address ? `${project.work_address.street}, ${project.work_address.number}` : '',
          scope: {
            total_area: project.scope?.total_area || '',
            rooms_included: project.scope?.rooms_included ? project.scope.rooms_included.join(', ') : '',
            technical_notes: project.scope?.technical_notes || ''
          },
          clientId: project.clients.map(c => c.id),
          status: project.status || 'draft',
        });
        this.projectStatus = project.status || 'draft';
        this.selectedClients = project.clients;
        this.etapasProjeto = project.stages ? project.stages.map((e: Stage) => ({ ...e })) : [];
        this.etapasVisuais = this.etapasProjeto.map(e => ({ id: e.id, active: true, expanded: false }));
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

    let work_address = undefined;
    if (typeof formValue.address === 'string' && formValue.address.trim()) {

      const [street, number] = formValue.address.split(',').map((v: string) => v.trim());
      work_address = { street: street || '', number: number || '' };
    } else if (formValue.address && typeof formValue.address === 'object') {
      work_address = formValue.address;
    }

    let scope = undefined;
    if (formValue.scope) {
      scope = {
        total_area: formValue.scope.total_area ? Number(formValue.scope.total_area) : undefined,
        rooms_included: formValue.scope.rooms_included
          ? (typeof formValue.scope.rooms_included === 'string'
              ? formValue.scope.rooms_included.split(',').map((r: string) => r.trim()).filter((r: string) => r)
              : formValue.scope.rooms_included)
          : [],
        technical_notes: formValue.scope.technical_notes || ''
      };
    }
    const data: any = {
      name: formValue.name,
      description: formValue.description,
      total_value: moedaBrToFloat(formValue.value),
      currency: 'BRL',
      start_date: formValue.startDate,
      estimated_end_date: formValue.endDate,
      clients: this.selectedClients.map(c => c.id),
      stages: this.etapasProjeto.map((s: Stage) => s.id),
      work_address,
      scope,
      status: formValue.status,
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

  adicionarEtapa(): void {
    this.openEtapaModal();
  }

  get stages(): Stage[] {
    return this.etapasProjeto;
  }

  statusLabel(status: string): string {
    return getStatusBadge(status).label;
  }
  statusBadgeClass(status: string): string {
    return 'status-badge ' + getStatusBadge(status).color;
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

function moedaBrToFloat(valor: string | number | undefined): number {
  if (valor === undefined || valor === null) return 0;
  if (typeof valor === 'number') return valor;
  if (typeof valor !== 'string') return 0;
  return parseFloat(valor.replace(/\./g, '').replace(',', '.'));
}
