import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import {RouterLink} from "@angular/router";
import {NgForOf, NgIf} from "@angular/common";

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
    imports: [
        RouterLink,
        NgForOf,
        NgIf
    ],
    styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  isCollapsed = false;

  menuItems: SidebarMenuItem[] = [
    {
      label: 'Dashboard',
      icon: 'dashboard',
      route: '/dashboard',
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

  constructor(private router: Router) {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.updateFavorite(event.urlAfterRedirects);
      }
    });
    this.updateFavorite(this.router.url);
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
