import { Component, inject, OnInit } from '@angular/core';
import { SharedModule } from './shared/shared.module';
import { AuthService } from './core/services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  imports: [SharedModule]
})
export class AppComponent implements OnInit {
  title = 'Crialt Arquitetura - Painel Administrativo';
  private readonly authService = inject(AuthService);

  ngOnInit(): void {
    this.authService.fetchCurrentUser().subscribe();
  }
}
