import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Observable } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private router: Router, private authService: AuthService) {}

  canActivate(): Observable<boolean> {
    return this.authService.fetchCurrentUser().pipe(
      map(user => {
        if (!!user) {
          return true;
        } else {
          this.router.navigate(['/auth/login']);
          return false;
        }
      }),
      catchError(() => {
        this.router.navigate(['/auth/login']);
        return [false];
      })
    );
  }
}
