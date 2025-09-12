import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ClientService } from '../../../core/services/client.service';
import { ProjectService } from '../../../core/services/project.service';
import { FileService } from '../../../core/services/file.service';
import { AuthService } from '../../../core/services/auth.service';
import { Client } from '../../../core/models/client.model';
import { Project } from '../../../core/models/project.model';
import { File } from '../../../core/models/file.model';
import { getStatusBadge } from '../../../core/models/status.model';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-client-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, LoadingSpinnerComponent],
  templateUrl: './client-detail.component.html',
  styleUrls: ['./client-detail.component.scss']
})
export class ClientDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly clientService = inject(ClientService);
  private readonly projectService = inject(ProjectService);
  private readonly fileService = inject(FileService);
  private readonly authService = inject(AuthService);

  client: Client | null = null;
  projects: Project[] = [];
  documents: File[] = [];
  loading = false;
  error = '';
  editMode = false;
  editData: Partial<Client> = {};
  passwordLoading = false;
  passwordError = '';
  passwordSuccess = '';
  canEdit = false;
  showPasswordCard = false;

  ngOnInit(): void {
    const clientId = this.route.snapshot.paramMap.get('id');
    this.authService.getCurrentUser().subscribe(user => {
      this.canEdit = !!user && (user.role === 'admin' || user.role === 'architect');
    });
    if (clientId) {
      this.loadClient(clientId);
    }
  }

  loadClient(id: string): void {
    this.loading = true;
    this.error = '';
    this.clientService.getClientById(id).subscribe({
      next: (client) => {
        this.client = client;
        this.editData = { ...client };
        this.loadProjects(client.id);
        this.loadDocuments(client.id);
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Erro ao buscar cliente.';
      }
    });
  }

  loadProjects(clientId: string): void {
    this.projectService.getProjects().subscribe({
      next: (projects) => {
        this.projects = projects.filter(p => p.clients.some(c => c.id === clientId));
      }
    });
  }

  loadDocuments(clientId: string): void {
    this.fileService.getFiles().subscribe({
      next: (files) => {
        this.documents = files.filter(f => f.client_id === clientId);
      }
    });
  }

  enableEdit(): void {
    this.editMode = true;
    this.editData = { ...this.client };
    this.showPasswordCard = false;
  }

  cancelEdit(): void {
    this.editMode = false;
    this.editData = { ...this.client };
    this.showPasswordCard = false;
  }

  togglePasswordCard(): void {
    this.showPasswordCard = !this.showPasswordCard;
    this.passwordError = '';
    this.passwordSuccess = '';
  }

  saveEdit(): void {
    if (!this.client) return;
    this.loading = true;
    this.clientService.updateClient(this.client.id, this.editData).subscribe({
      next: (updated) => {
        this.client = updated;
        this.editMode = false;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Erro ao salvar alterações.';
      }
    });
  }

  changePassword(newPassword: string): void {
    if (!this.client) return;
    this.passwordLoading = true;
    this.passwordError = '';
    this.passwordSuccess = '';
    this.clientService.resetPassword(this.client.id, newPassword).subscribe({
      next: (result) => {
        this.passwordSuccess = result.new_password ? `Nova senha: ${result.new_password}` : 'Senha redefinida com sucesso.';
        this.passwordLoading = false;
      },
      error: () => {
        this.passwordLoading = false;
        this.passwordError = 'Erro ao redefinir senha.';
      }
    });
  }

  public navigateToProject(projectId: string): void {
    this.router.navigate(['/projects', projectId]);
  }

  public downloadFile(docId: string): void {
    window.open(`/api/files/${docId}/download`, '_blank');
  }

  onBack(): void {
    this.router.navigate(['/clients']);
  }

  statusLabel(status: string): string {
    return getStatusBadge(status as any).label;
  }
  statusBadgeClass(status: string): string {
    return 'status-badge ' + getStatusBadge(status).color;
  }
}
