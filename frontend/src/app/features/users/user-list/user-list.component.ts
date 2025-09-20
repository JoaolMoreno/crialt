import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { User } from '../../../core/models/user.model';
import { UserService } from '../../../core/services/user.service';
import { SharedModule } from '../../../shared/shared.module';
import { NotificationService } from '../../../shared/notification.service';

@Component({
  selector: 'app-user-list',
  standalone: true,
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.scss'],
  imports: [SharedModule]
})
export class UserListComponent implements OnInit {
  private readonly userService = inject(UserService);
  private readonly router = inject(Router);
  private readonly notification = inject(NotificationService);

  users: User[] = [];
  total = 0;
  pageSize = 10;
  currentPage = 1;
  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';
  searchQuery = '';
  selectedRole = '';
  selectedStatus = '';
  loading = false;

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading = true;
    const params: Record<string, any> = {
      limit: this.pageSize,
      offset: (this.currentPage - 1) * this.pageSize,
      order_by: this.sortColumn || 'created_at',
      order_dir: this.sortDirection,
      role: this.selectedRole || undefined,
      is_active: this.selectedStatus || undefined,
      search: this.searchQuery || undefined
    };
    this.userService.getUsers(params).subscribe({
      next: (res) => {
        this.users = res.items;
        this.total = res.total;
        this.loading = false;
      },
      error: (err) => {
        this.notification.error(err);
        this.loading = false;
      }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadUsers();
  }

  onSortChange(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.loadUsers();
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadUsers();
  }

  onNewUser(): void {
    this.router.navigate(['/users/new']);
  }

  onEditUser(user: User): void {
    this.router.navigate([`/users/${user.id}/edit`]);
  }

  onToggleStatus(user: User): void {
    this.loading = true;
    const action = user.is_active ? this.userService.deactivateUser(user.id) : this.userService.activateUser(user.id);
    action.subscribe({
      next: () => this.loadUsers(),
      error: () => this.loading = false
    });
  }

  onResetPassword(user: User): void {
    if (confirm(`Deseja redefinir a senha do usuário "${user.name}"?`)) {
      this.loading = true;
      this.userService.resetPassword(user.id).subscribe({
        next: (result) => {
          alert(`Nova senha gerada: ${result.new_password}`);
          this.loading = false;
        },
        error: () => {
          this.loading = false;
        }
      });
    }
  }
}
