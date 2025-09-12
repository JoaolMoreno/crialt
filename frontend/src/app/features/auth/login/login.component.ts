import { Component, inject } from '@angular/core';
import { AuthService } from '../../../core/services/auth.service';
import {Router} from '@angular/router';
import { SharedModule } from '../../../shared/shared.module';
import {NgOptimizedImage} from "@angular/common";

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  imports: [SharedModule, NgOptimizedImage]
})
export class LoginComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  username = '';
  password = '';
  loading = false;
  errorMessage = '';

  onSubmit(): void {
    if (!this.username || !this.password) {
      this.errorMessage = 'Preencha todos os campos.';
      return;
    }
    this.loading = true;
    this.errorMessage = '';
    this.authService.login({
        username: this.username,
        password: this.password
    }).subscribe({
      next: (user) => {
        this.loading = false;
        this.authService.setCurrentUser(user);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Credenciais inválidas ou usuário inativo.';
      }
    });
  }
}
