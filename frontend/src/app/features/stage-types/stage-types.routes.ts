import { Routes } from '@angular/router';

export const stageTypesRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./stage-type-list/stage-type-list.component').then(m => m.StageTypeListComponent),
    title: 'Etapas'
  },
  {
    path: 'new',
    loadComponent: () => import('./stage-type-form/stage-type-form.component').then(m => m.StageTypeFormComponent),
    title: 'Nova Etapa'
  },
  {
    path: ':id',
    loadComponent: () => import('./stage-type-detail/stage-type-detail.component').then(m => m.StageTypeDetailComponent),
    title: 'Detalhes da Etapa'
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./stage-type-form/stage-type-form.component').then(m => m.StageTypeFormComponent),
    title: 'Editar Etapa'
  }
];
