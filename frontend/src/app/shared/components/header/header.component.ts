import { Component, inject } from '@angular/core';
import { AuthService } from '../../../core/services/auth.service';
import {Router, RouterLink} from '@angular/router';
import { FormsModule } from '@angular/forms';
import {AsyncPipe, NgForOf, NgIf} from "@angular/common";

interface HeaderMenuItem {
  label: string;
  icon: string;
  route: string;
}

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
    imports: [FormsModule, RouterLink, NgForOf, NgIf, AsyncPipe]
})
export class HeaderComponent {
  menuItems: HeaderMenuItem[] = [
    // { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    // { label: 'Clientes', icon: 'groups', route: '/clients' },
    // { label: 'Projetos', icon: 'folder_special', route: '/projects' },
    // { label: 'Etapas', icon: 'timeline', route: '/stages' },
    // { label: 'Arquivos', icon: 'attach_file', route: '/files' },
    // { label: 'Configurações', icon: 'settings', route: '/settings' }
  ];

  notificationsCount = 3;

  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  user = {
    name: 'João Silva',
    avatar: '/assets/images/avatar-default.png',
    role: 'admin'
  };

  breadcrumb: string[] = ['Dashboard'];

  searchQuery = '';

  get user$() {
    return this.authService.user$;
  }

  onProfileAction(action: string) {
    // Implementar ações do perfil (logout, perfil, etc)
  }

  onLogout() {
    this.authService.logout();
    this.router.navigate(['/auth/login']);
  }
}
