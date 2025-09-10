import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { User } from '../../../core/models/user.model';
import { UserService } from '../../../core/services/user.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-user-list',
  standalone: true,
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.scss'],
  imports: [FormsModule]
})
export class UserListComponent implements OnInit {
  private readonly userService = inject(UserService);
  private readonly router = inject(Router);

  users: User[] = [];
  filteredUsers: User[] = [];
  loading = false;
  searchQuery = '';
  selectedRole = '';
  selectedStatus = '';

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading = true;
    this.userService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.applyFilters();
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    this.filteredUsers = this.users.filter(user => {
      const matchesSearch = this.searchQuery ? (
        user.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(this.searchQuery.toLowerCase())
      ) : true;
      const matchesRole = this.selectedRole ? user.role === this.selectedRole : true;
      const matchesStatus = this.selectedStatus ? (
        this.selectedStatus === 'active' ? user.is_active : !user.is_active
      ) : true;
      return matchesSearch && matchesRole && matchesStatus;
    });
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

  ngOnChanges(): void {
    this.applyFilters();
  }
}
