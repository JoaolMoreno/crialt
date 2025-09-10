import { Component } from '@angular/core';
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
      notificationCount: 0
    },
    {
      label: 'Projetos',
      icon: 'folder_special',
      route: '/projects',
      notificationCount: 0
    },
    {
      label: 'Etapas',
      icon: 'timeline',
      route: '/stages'
    },
    {
      label: 'Arquivos',
      icon: 'attach_file',
      route: '/files'
    },
    {
      label: 'Configurações',
      icon: 'settings',
      route: '/settings'
    }
  ];

  toggleCollapse() {
    this.isCollapsed = !this.isCollapsed;
  }
}
