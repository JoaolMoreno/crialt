import { Component, inject, OnInit } from '@angular/core';
import { ClientService } from '../../../core/services/client.service';
import { Client } from '../../../core/models/client.model';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { FormsModule } from '@angular/forms';
import {DatePipe, NgForOf, NgIf} from "@angular/common";
import {LoadingSpinnerComponent} from "../../../shared/components/loading-spinner/loading-spinner.component";

@Component({
  selector: 'app-client-list',
  standalone: true,
  templateUrl: './client-list.component.html',
  styleUrls: ['./client-list.component.scss'],
    imports: [FormsModule, DatePipe, LoadingSpinnerComponent, NgIf, NgForOf]
})
export class ClientListComponent implements OnInit {
  private readonly clientService = inject(ClientService);
  private readonly router = inject(Router);
  private readonly authService = inject(AuthService);

  clients: Client[] = [];
  filteredClients: Client[] = [];
  loading = false;
  error = '';
  searchQuery = '';
  selectedStatus = '';
  selectedDocumentType = '';
  selectedDate = '';
  isAdmin = false;

  ngOnInit(): void {
    this.authService.getCurrentUser().subscribe(user => {
      this.isAdmin = user?.role === 'admin';
    });
    this.loadClients();
  }

  loadClients(): void {
    this.loading = true;
    this.error = '';
    this.clientService.getClients().subscribe({
      next: (clients) => {
        this.clients = clients;
        this.applyFilters();
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Erro ao buscar clientes.';
      }
    });
  }

  applyFilters(): void {
    this.filteredClients = this.clients.filter(client => {
      const matchesSearch = this.searchQuery ? (
        client.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        client.document.toLowerCase().includes(this.searchQuery.toLowerCase())
      ) : true;
      const matchesStatus = this.selectedStatus ? (
        this.selectedStatus === 'active' ? client.is_active : !client.is_active
      ) : true;
      const matchesDocumentType = this.selectedDocumentType ? client.document_type === this.selectedDocumentType : true;
      const matchesDate = this.selectedDate ? client.created_at.startsWith(this.selectedDate) : true;
      return matchesSearch && matchesStatus && matchesDocumentType && matchesDate;
    });
  }

  onEditClient(client: Client): void {
    if (this.isAdmin) {
      this.router.navigate([`/clients/${client.id}/edit`]);
    }
  }

  onViewClient(client: Client): void {
    this.router.navigate([`/clients/${client.id}`]);
  }

  onToggleStatus(client: Client): void {
    if (!this.isAdmin) return;
    this.loading = true;
    const updated = { ...client, is_active: !client.is_active };
    this.clientService.updateClient(client.id, updated).subscribe({
      next: () => this.loadClients(),
      error: () => this.loading = false
    });
  }

  onNewProject(client: Client): void {
    this.router.navigate(['/projects/new'], { queryParams: { clientId: client.id } });
  }

  onExport(): void {
    // Implementar exportação para Excel/PDF
  }

  ngOnChanges(): void {
    this.applyFilters();
  }
}
