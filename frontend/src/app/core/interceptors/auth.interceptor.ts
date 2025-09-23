import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private router: Router) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Adiciona withCredentials em todas as requisições, exceto login/registro
    const isAuthEndpoint = req.url.includes('/auth/login') || req.url.includes('/auth/register');
    const authReq = isAuthEndpoint ? req : req.clone({ withCredentials: true });

    return next.handle(authReq).pipe(
      catchError(err => {
        // Só redirecionar para login se for uma requisição de autenticação crítica
        // Não redirecionar para operações de CRUD como delete de arquivos
        const isCriticalAuthRequest = req.url.includes('/users/me') ||
                                    req.url.includes('/clients/me') ||
                                    req.url.includes('/auth/');

        if ((err.status === 401 || err.status === 403) && isCriticalAuthRequest) {
          console.warn('[AuthInterceptor] Redirecionando para login devido a erro de autenticação em:', req.url);
          this.router.navigate(['/auth/login']);
        }

        // Sempre propagar o erro para o componente tratar
        return throwError(() => err);
      })
    );
  }
}
