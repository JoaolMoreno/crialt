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
                path: 'home',
                loadChildren: () => import('./features/dashboard/dashboard.routes').then(m => m.dashboardRoutes)
            },
            {
                path: 'clients',
                loadChildren: () => import('./features/clients/clients.routes').then(m => m.clientsRoutes)
            },
            {
                path: 'projects',
                loadChildren: () => import('./features/projects/projects.routes').then(m => m.projectsRoutes)
            },
            {
                path: 'files',
                loadChildren: () => import('./features/files/files.routes').then(m => m.filesRoutes)
            },
            {
                path: 'stages',
                loadChildren: () => import('./features/stage-types/stage-types.routes').then(m => m.stageTypesRoutes)
            },
            {
                path: '',
                redirectTo: 'home',
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
        redirectTo: 'home'
    }
];
