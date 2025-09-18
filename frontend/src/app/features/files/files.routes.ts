import { Routes } from '@angular/router';

export const filesRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./file-list/file-list.component').then(m => m.FileListComponent),
    title: 'Arquivos'
  }
];
