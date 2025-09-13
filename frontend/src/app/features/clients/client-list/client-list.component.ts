import { Component, inject, OnInit } from '@angular/core';
import { ClientService } from '../../../core/services/client.service';
import { Client } from '../../../core/models/client.model';
import { Router } from '@angular/router';
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

  clients: Client[] = [];
  total = 0;
  pageSize = 10;
  currentPage = 1;
  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';
  searchQuery = '';
  selectedStatus = '';
  selectedDate = '';
  loading = false;
  error = '';

  ngOnInit(): void {
    this.loadClients();
  }

  loadClients(): void {
    this.loading = true;
    this.error = '';
    const params: Record<string, any> = {
      limit: this.pageSize,
      offset: (this.currentPage - 1) * this.pageSize,
      order_by: this.sortColumn || 'created_at',
      order_dir: this.sortDirection,
      name: this.searchQuery || undefined,
      is_active: this.selectedStatus === 'active' ? true : this.selectedStatus === 'inactive' ? false : undefined,
      created_at: this.selectedDate || undefined
    };
    this.clientService.getClients(params).subscribe({
      next: (res) => {
        this.clients = res.items;
        this.total = res.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Erro ao buscar clientes.';
      }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadClients();
  }

  onSortChange(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.loadClients();
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadClients();
  }

  onEditClient(client: Client): void {
    this.router.navigate([`/clients/${client.id}/edit`]);
  }

  onViewClient(client: Client): void {
    this.router.navigate([`/clients/${client.id}`]);
  }

  onToggleStatus(client: Client): void {
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
}
