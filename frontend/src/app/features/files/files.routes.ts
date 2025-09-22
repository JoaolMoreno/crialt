import { Routes } from '@angular/router';
import { RoleGuard } from '../../core/guards/role.guard';

export const filesRoutes: Routes = [
  {
    path: '',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./file-list/file-list.component').then(m => m.FileListComponent),
    title: 'Arquivos'
  }
];
