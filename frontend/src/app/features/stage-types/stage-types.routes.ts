import { Routes } from '@angular/router';
import { RoleGuard } from '../../core/guards/role.guard';

export const stageTypesRoutes: Routes = [
  {
    path: '',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./stage-type-list/stage-type-list.component').then(m => m.StageTypeListComponent),
    title: 'Etapas'
  },
  {
    path: 'new',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./stage-type-form/stage-type-form.component').then(m => m.StageTypeFormComponent),
    title: 'Nova Etapa'
  },
  {
    path: ':id',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./stage-type-detail/stage-type-detail.component').then(m => m.StageTypeDetailComponent),
    title: 'Detalhes da Etapa'
  },
  {
    path: ':id/edit',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./stage-type-form/stage-type-form.component').then(m => m.StageTypeFormComponent),
    title: 'Editar Etapa'
  }
];
