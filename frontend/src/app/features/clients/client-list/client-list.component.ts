import { Component, inject, OnInit } from '@angular/core';
import { ClientService } from '../../../core/services/client.service';
import { Client } from '../../../core/models/client.model';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { SharedModule } from '../../../shared/shared.module';

@Component({
  selector: 'app-client-list',
  standalone: true,
  templateUrl: './client-list.component.html',
  styleUrls: ['./client-list.component.scss'],
  imports: [SharedModule]
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

  // Paginação
  pageSize = 10;
  currentPage = 1;
  totalPages = 1;
  // Ordenação
  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';

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

  get paginatedClients(): Client[] {
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    return this.filteredClients.slice(start, end);
  }

  setPage(page: number): void {
    if (page < 1 || page > this.totalPages) return;
    this.currentPage = page;
  }

  sortBy(column: 'name' | 'document' | 'email' | 'is_active' | 'created_at'): void {
    const validColumns = {
      name: (c: Client) => c.name,
      document: (c: Client) => c.document,
      email: (c: Client) => c.email,
      is_active: (c: Client) => c.is_active,
      created_at: (c: Client) => c.created_at
    };
    if (!validColumns[column]) return;
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.filteredClients.sort((a, b) => {
      let valA = validColumns[column](a);
      let valB = validColumns[column](b);
      if (typeof valA === 'string') valA = valA.toLowerCase();
      if (typeof valB === 'string') valB = valB.toLowerCase();
      if (valA < valB) return this.sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return this.sortDirection === 'asc' ? 1 : -1;
      return 0;
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
    this.totalPages = Math.max(1, Math.ceil(this.filteredClients.length / this.pageSize));
    this.currentPage = 1;
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
    // Mock: exportação de clientes para Excel
    alert('Exportação de clientes para Excel está em desenvolvimento.');
  }

  onNewClient(): void {
    this.router.navigate(['/clients/new']);
  }

  ngOnChanges(): void {
    this.applyFilters();
  }
}
