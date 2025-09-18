import { Routes } from '@angular/router';

export const clientsRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./client-list/client-list.component').then(m => m.ClientListComponent),
    title: 'Clientes'
  },
  {
    path: 'new',
    loadComponent: () => import('./client-form/client-form.component').then(m => m.ClientFormComponent),
    title: 'Novo Cliente'
  },
  {
    path: ':id',
    loadComponent: () => import('./client-detail/client-detail.component').then(m => m.ClientDetailComponent),
    title: 'Detalhes do Cliente'
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./client-form/client-form.component').then(m => m.ClientFormComponent),
    title: 'Editar Cliente'
  }
];
