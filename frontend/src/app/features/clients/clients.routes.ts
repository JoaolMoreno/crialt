import { Routes } from '@angular/router';
import { RoleGuard } from '../../core/guards/role.guard';

export const clientsRoutes: Routes = [
  {
    path: '',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./client-list/client-list.component').then(m => m.ClientListComponent),
    title: 'Clientes'
  },
  {
    path: 'new',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./client-form/client-form.component').then(m => m.ClientFormComponent),
    title: 'Novo Cliente'
  },
  {
    path: ':id',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./client-detail/client-detail.component').then(m => m.ClientDetailComponent),
    title: 'Detalhes do Cliente'
  },
  {
    path: ':id/edit',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./client-form/client-form.component').then(m => m.ClientFormComponent),
    title: 'Editar Cliente'
  }
];
