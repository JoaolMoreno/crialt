import { Routes } from '@angular/router';
import { RoleGuard } from '../../core/guards/role.guard';

export const dashboardRoutes: Routes = [
  {
    path: '',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./dashboard.component').then(m => m.DashboardComponent),
    title: 'Dashboard'
  }
];
