import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { SharedModule } from '../../shared.module';
import { AuthService } from '../../../core/services/auth.service';

interface SidebarMenuItem {
  label: string;
  icon: string;
  route: string;
  notificationCount?: number;
  favorite?: boolean;
  children?: SidebarMenuItem[];
}

@Component({
    selector: 'app-sidebar',
    templateUrl: './sidebar.component.html',
    imports: [SharedModule],
    styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  isCollapsed = false;
  isMobile = false;

  menuItems: SidebarMenuItem[] = [
    {
      label: 'Home',
      icon: 'dashboard',
      route: '/home',
      favorite: true
    },
    {
      label: 'Clientes',
      icon: 'groups',
      route: '/clients',
      notificationCount: 0,
    },
    {
      label: 'Projetos',
      icon: 'folder_special',
      route: '/projects',
      notificationCount: 0,
    },
    {
      label: 'Etapas',
      icon: 'timeline',
      route: '/stages',
    },
    {
      label: 'Arquivos',
      icon: 'attach_file',
      route: '/files',
    },
    {
      label: 'Configurações',
      icon: 'settings',
      route: '/settings',
    }
  ];

  constructor(private router: Router, private authService: AuthService) {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.updateFavorite(event.urlAfterRedirects);
      }
    });
    this.updateFavorite(this.router.url);
    this.checkMobile();
    window.addEventListener('resize', this.checkMobile.bind(this));

    // Ajusta menu para cliente
    if (this.authService.isClientLogged()) {
      this.menuItems = [
        {
          label: 'Home',
          icon: 'dashboard',
          route: '/home',
          favorite: true
        },
        {
          label: 'Projetos',
          icon: 'folder_special',
          route: '/projects',
          notificationCount: 0,
        }
      ];
    }
  }

  checkMobile() {
    this.isMobile = window.innerWidth <= 768;
  }

  updateFavorite(currentRoute: string) {
    const cleanRoute = currentRoute.split('?')[0].split('#')[0];
    const firstSegment = '/' + cleanRoute.split('/').filter(Boolean)[0];
    this.menuItems = this.menuItems.map(item => ({
      ...item,
      favorite: item.route === firstSegment
    }));
  }

  toggleCollapse() {
    this.isCollapsed = !this.isCollapsed;
  }
}
