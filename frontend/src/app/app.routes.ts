import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { AuthLayoutComponent } from './layout/auth-layout/auth-layout.component';
import { AuthGuard } from './core/guards/auth.guard';
import { RoleGuard } from './core/guards/role.guard';
export const appRoutes: Routes = [
    {
        path: '',
        component: MainLayoutComponent,
        canActivate: [AuthGuard],
        children: [
            {
                path: 'dashboard',
                loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'clients',
                loadComponent: () => import('./features/clients/client-list/client-list.component').then(m => m.ClientListComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'clients/new',
                loadComponent: () => import('./features/clients/client-form/client-form.component').then(m => m.ClientFormComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'clients/:id',
                loadComponent: () => import('./features/clients/client-detail/client-detail.component').then(m => m.ClientDetailComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'clients/:id/edit',
                loadComponent: () => import('./features/clients/client-form/client-form.component').then(m => m.ClientFormComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'projects',
                loadComponent: () => import('./features/projects/project-list/project-list.component').then(m => m.ProjectListComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'projects/new',
                loadComponent: () => import('./features/projects/project-form/project-form.component').then(m => m.ProjectFormComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'projects/:id',
                loadComponent: () => import('./features/projects/project-detail/project-detail.component').then(m => m.ProjectDetailComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'projects/:id/edit',
                loadComponent: () => import('./features/projects/project-form/project-form.component').then(m => m.ProjectFormComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'projects/:id/timeline',
                loadComponent: () => import('./features/projects/project-timeline/project-timeline.component').then(m => m.ProjectTimelineComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'files',
                loadComponent: () => import('./features/files/file-list/file-list.component').then(m => m.FileListComponent),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
            },
            {
                path: 'stages',
                loadChildren: () => import('./features/stage-types/stage-types.routes').then(m => m.stageTypesRoutes),
                canActivate: [RoleGuard],
                data: { allowedRoles: ['admin'] }
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
