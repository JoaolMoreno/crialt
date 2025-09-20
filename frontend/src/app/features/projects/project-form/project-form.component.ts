import { Component, inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ProjectService } from '../../../core/services/project.service';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { ClientService } from '../../../core/services/client.service';
import { Client } from '../../../core/models/client.model';
import { StageTypeService } from '../../../core/services/stage-type.service';
import { StageType } from '../../../core/models/stage-type.model';
import { getStatusBadge } from '../../../core/models/status.model';
import { SharedModule } from "../../../shared/shared.module";
import { Subject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';
import { Stage } from "../../../core/models/stage.model";
import { FileUploadComponent } from "../../../shared/components/file-upload/file-upload.component";
import { FileUpload } from '../../../core/services/file.service';
import { NotificationService } from '../../../shared/notification.service';

@Component({
    selector: 'app-project-form',
    standalone: true,
    templateUrl: './project-form.component.html',
    imports: [SharedModule, FileUploadComponent],
    styleUrls: ['./project-form.component.scss']
})
export class ProjectFormComponent {
  isEdit = false;
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly projectService = inject(ProjectService);
  private readonly fb = inject(FormBuilder);
  private readonly notification = inject(NotificationService);

  form: FormGroup;
  loading = false;
  projectId: string | null = null;

  clients: Client[] = [];
  selectedClients: Client[] = [];
  showClientModal = false;
  clientSearch = '';
  loadingClients = false;

  etapasDisponiveis: StageType[] = [];
  etapasProjeto: Stage[] = [];
  showEtapaModal = false;
  etapaSearch = '';
  etapasSelecionadas: StageType[] = [];

  private readonly clientService = inject(ClientService);
  private readonly stageTypeService = inject(StageTypeService);

  etapasVisuais: { id: string; active: boolean; expanded: boolean }[] = [];

  editProjectStatus = false;
  projectStatus: string = 'draft';
  editStageStatus: { [id: string]: boolean } = {};

  private clientSearchSubject = new Subject<string>();
  private clientSearchRequestId = 0;
  private lastClientSearchRequestId = 0;

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
    this.loadStages();

    this.clientSearchSubject.pipe(debounceTime(3000)).subscribe(search => {
      this.lastClientSearchRequestId++;
      this.buscarClientes(search, this.lastClientSearchRequestId);
    });
  }

  toggleEditProjectStatus(): void {
    this.editProjectStatus = !this.editProjectStatus;
    if (!this.editProjectStatus) {
      this.form.get('status')?.setValue(this.projectStatus);
    }
  }

  saveProjectStatus(): void {
    this.projectStatus = this.form.get('status')?.value;
    this.editProjectStatus = false;
  }

  toggleEditStageStatus(id: string): void {
    this.editStageStatus[id] = !this.editStageStatus[id];
  }

  saveStageStatus(id: string): void {
    this.editStageStatus[id] = false;
  }

  openClientModal(): void {
    this.showClientModal = true;
    this.clientSearch = '';
    this.lastClientSearchRequestId++;
    this.buscarClientes('', this.lastClientSearchRequestId);
  }

  buscarClientes(search: string, requestId?: number): void {
    this.loadingClients = true;
    const currentRequestId = requestId ?? ++this.clientSearchRequestId;
    this.clientService.getClients({ search }).subscribe({
      next: (result) => {
        if (currentRequestId === this.lastClientSearchRequestId) {
          this.clients = result.items;
        }
        this.loadingClients = false;
      },
      error: (err) => {
        if (currentRequestId === this.lastClientSearchRequestId) {
          this.clients = [];
        }
        this.loadingClients = false;
        this.notification.error(err);
      }
    });
  }

  onClientSearchChange(): void {
    this.clientSearchSubject.next(this.clientSearch);
  }

  closeClientModal(): void {
    this.showClientModal = false;
  }

  get filteredClients(): Client[] {
    return this.clients;
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
    this.stageTypeService.getStageTypes({ is_active: true }).subscribe({
      next: (result) => {
        this.etapasDisponiveis = result.items;
        this.loadingStages = false;
      },
      error: (err) => {
        this.loadingStages = false;
        this.notification.error(err);
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

        this.etapasProjeto = project.stages
          ? project.stages
              .map((e: Stage) => ({ ...e }))
              .sort((a, b) => a.order - b.order)
          : [];

        this.etapasVisuais = this.etapasProjeto.map(e => ({ id: e.id, active: true, expanded: false }));
        this.loading = false;
      },
      error: (err) => {
        this.notification.error(err);
        this.loading = false;
      }
    });
  }

  formatValueInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    let value = input.value.replace(/\D/g, '');
    value = value.replace(/^0+/, '');
    if (!value) {
      input.value = '';
      this.form.get('value')?.setValue('');
      return;
    }
    while (value.length < 3) value = '0' + value;
    const intPart = value.slice(0, value.length - 2);
    const decPart = value.slice(-2);
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

    let stages = undefined;
    if (this.etapasProjeto.length > 0) {
      stages = this.etapasProjeto.map((stage) => {
        const stageData: any = {
          stage_type_id: stage.stage_type_id,
          name: stage.name,
          description: stage.description,
          order: stage.order,
          planned_start_date: stage.planned_start_date,
          planned_end_date: stage.planned_end_date,
          value: stage.value || 0,
          progress_percentage: stage.progress_percentage || 0,
          notes: stage.notes || ''
        };

        if (this.isEdit && stage.id && !stage.id.startsWith('temp_')) {
          stageData.id = stage.id;
          stageData.status = stage.status;
          stageData.actual_start_date = stage.actual_start_date;
          stageData.actual_end_date = stage.actual_end_date;
          stageData.assigned_to_id = stage.assigned_to_id;
        }

        return stageData;
      });
    }

    const data: any = {
      name: formValue.name,
      description: formValue.description,
      total_value: moedaBrToFloat(formValue.value),
      currency: 'BRL',
      start_date: formValue.startDate,
      estimated_end_date: formValue.endDate,
      clients: this.selectedClients.map(c => c.id),
      work_address,
      scope,
      status: formValue.status,
    };

    if (stages) {
      data.stages = stages;
    }

    if (this.isEdit && this.projectId) {
      this.projectService.updateProject(this.projectId, data).subscribe({
        next: () => {
          this.router.navigate(['/projects']);
        },
        error: (err) => {
          this.notification.error(err);
          this.loading = false;
        }
      });
    } else {
      this.projectService.createProject(data).subscribe({
        next: () => {
          this.router.navigate(['/projects']);
        },
        error: (err) => {
          this.notification.error(err);
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

  get filteredEtapas(): StageType[] {
    if (!this.etapaSearch) return this.etapasDisponiveis;
    return this.etapasDisponiveis.filter(etapa =>
      etapa.name.toLowerCase().includes(this.etapaSearch.toLowerCase())
    );
  }

  toggleEtapaSelection(etapa: StageType): void {
    const idx = this.etapasSelecionadas.findIndex(e => e.id === etapa.id);
    if (idx >= 0) {
      this.etapasSelecionadas.splice(idx, 1);
    } else {
      this.etapasSelecionadas.push(etapa);
    }
  }

  isEtapaSelected(etapa: StageType): boolean {
    return this.etapasSelecionadas.some(e => e.id === etapa.id);
  }

  confirmarEtapas(): void {
    this.etapasSelecionadas.forEach((etapaType, index) => {
      const novaEtapa: Stage = {
        id: this.generateTempId(),
        name: etapaType.name,
        description: etapaType.description || '',
        order: this.etapasProjeto.length + index + 1,
        status: 'pending',
        planned_start_date: this.form.get('startDate')?.value || new Date().toISOString().split('T')[0],
        actual_start_date: undefined,
        planned_end_date: this.form.get('endDate')?.value || new Date().toISOString().split('T')[0],
        actual_end_date: undefined,
        value: 0,
        specific_data: undefined,
        progress_percentage: 0,
        notes: '',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        project_id: this.projectId || '',
        stage_type_id: etapaType.id,
        created_by_id: '',
        assigned_to_id: undefined,
        files: [],
        tasks: [],
        stage_type: etapaType
      };

      this.etapasProjeto.push(novaEtapa);
      this.etapasVisuais.push({ id: novaEtapa.id, active: true, expanded: false });
    });

    this.closeEtapaModal();
  }

  private generateTempId(): string {
    return 'temp_' + Math.random().toString(36).substr(2, 9);
  }

  reordenarEtapas(etapaId: string, direcao: 'up' | 'down'): void {
    const index = this.etapasProjeto.findIndex(e => e.id === etapaId);
    if (index === -1) return;

    const newIndex = direcao === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= this.etapasProjeto.length) return;

    [this.etapasProjeto[index], this.etapasProjeto[newIndex]] =
    [this.etapasProjeto[newIndex], this.etapasProjeto[index]];

    this.etapasProjeto.forEach((etapa, idx) => {
      etapa.order = idx + 1;
    });
  }

  onFilesChanged(files: FileUpload[]): void {
    // Pode ser usado para atualizar a UI ou validar arquivos
    console.log('Arquivos atualizados:', files);
  }
}

function moedaBrValidator(control: AbstractControl): ValidationErrors | null {
  const value = control.value;
  if (!value) {
    return { required: true };
  }
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
