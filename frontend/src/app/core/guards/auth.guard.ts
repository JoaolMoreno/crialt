import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private router: Router, private authService: AuthService) {}

  canActivate(): Observable<boolean> {
    console.log('[AuthGuard] canActivate: verificando usuário logado');
    return this.authService.fetchCurrentUser().pipe(
      map(user => {
        if (!!user) {
          console.log('[AuthGuard] canActivate: usuário autenticado', user);
          return true;
        } else {
          console.warn('[AuthGuard] canActivate: usuário não autenticado, redirecionando para login');
          this.router.navigate(['/auth/login']);
          return false;
        }
      }),
      catchError((err) => {
        console.error('[AuthGuard] canActivate: erro ao buscar usuário', err);
        this.router.navigate(['/auth/login']);
        return of(false);
      })
    );
  }
}
