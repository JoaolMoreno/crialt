import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { AuthLayoutComponent } from './layout/auth-layout/auth-layout.component';
import { AuthGuard } from './core/guards/auth.guard';
export const appRoutes: Routes = [
    {
        path: '',
        component: MainLayoutComponent,
        canActivate: [AuthGuard],
        children: [
            {
                path: 'dashboard',
                loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent)
            },
            {
                path: 'clients',
                loadComponent: () => import('./features/clients/client-list/client-list.component').then(m => m.ClientListComponent)
            },
            {
                path: 'clients/new',
                loadComponent: () => import('./features/clients/client-form/client-form.component').then(m => m.ClientFormComponent)
            },
            {
                path: 'clients/:id',
                loadComponent: () => import('./features/clients/client-detail/client-detail.component').then(m => m.ClientDetailComponent)
            },
            {
                path: 'clients/:id/edit',
                loadComponent: () => import('./features/clients/client-form/client-form.component').then(m => m.ClientFormComponent)
            },
            {
                path: 'projects',
                loadComponent: () => import('./features/projects/project-list/project-list.component').then(m => m.ProjectListComponent)
            },
            {
                path: 'projects/new',
                loadComponent: () => import('./features/projects/project-form/project-form.component').then(m => m.ProjectFormComponent)
            },
            {
                path: 'stages',
                loadComponent: () => import('./features/stages/stage-form/stage-form.component').then(m => m.StageFormComponent)
            },
            {
                path: 'files',
                loadComponent: () => import('./features/files/file-list/file-list.component').then(m => m.FileListComponent)
            },
            {
                path: '',
                redirectTo: 'dashboard',
                pathMatch: 'full'
            }
        ]
    },
    {
        path: 'auth',
        component: AuthLayoutComponent,
        children: [
            {
                path: 'login',
                loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
            },
            {
                path: 'register',
                loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent)
            },
            {
                path: '',
                redirectTo: 'login',
                pathMatch: 'full'
            }
        ]
    },
    {
        path: '**',
        redirectTo: 'dashboard'
    }
];
