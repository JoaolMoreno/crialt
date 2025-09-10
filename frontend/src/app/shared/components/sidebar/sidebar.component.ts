import { Component } from '@angular/core';

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
      notificationCount: 2
    },
    {
      label: 'Projetos',
      icon: 'folder_special',
      route: '/projects',
      notificationCount: 1
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
