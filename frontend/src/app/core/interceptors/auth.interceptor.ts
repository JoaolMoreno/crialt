import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
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
        if (err.status === 401 || err.status === 403) {
          this.router.navigate(['/auth/login']);
        }
        throw err;
      })
    );
  }
}
