import { Routes } from '@angular/router';
import { RoleGuard } from '../../core/guards/role.guard';

export const projectsRoutes: Routes = [
  {
    path: '',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin', 'client'] },
    loadComponent: () => import('./project-list/project-list.component').then(m => m.ProjectListComponent),
    title: 'Projetos'
  },
  {
    path: 'new',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./project-form/project-form.component').then(m => m.ProjectFormComponent),
    title: 'Novo Projeto'
  },
  {
    path: ':id',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin', 'client'] },
    loadComponent: () => import('./project-detail/project-detail.component').then(m => m.ProjectDetailComponent),
    title: 'Detalhes do Projeto'
  },
  {
    path: ':id/edit',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin'] },
    loadComponent: () => import('./project-form/project-form.component').then(m => m.ProjectFormComponent),
    title: 'Editar Projeto'
  },
  {
    path: ':id/timeline',
    canActivate: [RoleGuard],
    data: { allowedRoles: ['admin','client'] },
    loadComponent: () => import('./project-timeline/project-timeline.component').then(m => m.ProjectTimelineComponent),
    title: 'Timeline do Projeto'
  }
];
