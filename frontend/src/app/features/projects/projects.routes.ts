import { Routes } from '@angular/router';

export const projectsRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./project-list/project-list.component').then(m => m.ProjectListComponent),
    title: 'Projetos'
  },
  {
    path: 'new',
    loadComponent: () => import('./project-form/project-form.component').then(m => m.ProjectFormComponent),
    title: 'Novo Projeto'
  },
  {
    path: ':id',
    loadComponent: () => import('./project-detail/project-detail.component').then(m => m.ProjectDetailComponent),
    title: 'Detalhes do Projeto'
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./project-form/project-form.component').then(m => m.ProjectFormComponent),
    title: 'Editar Projeto'
  },
  {
    path: ':id/timeline',
    loadComponent: () => import('./project-timeline/project-timeline.component').then(m => m.ProjectTimelineComponent),
    title: 'Timeline do Projeto'
  }
];
