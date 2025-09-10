import { Component, inject } from '@angular/core';
import { AuthService } from '../../../core/services/auth.service';
import {Router, RouterLink} from '@angular/router';
import { FormsModule } from '@angular/forms';
import {LoadingSpinnerComponent} from "../../../shared/components/loading-spinner/loading-spinner.component";
import {NgIf} from "@angular/common";

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
    imports: [FormsModule, LoadingSpinnerComponent, RouterLink, NgIf]
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
