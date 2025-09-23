import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class RoleGuard implements CanActivate {
  constructor(private router: Router, private authService: AuthService) {}

  canActivate(route: ActivatedRouteSnapshot): Observable<boolean> {
    const allowedRoles = route.data['allowedRoles'] as string[] || [];

    return this.authService.checkToken().pipe(
      map(payload => {
        const normalizedAllowedRoles = allowedRoles.map(r => r.trim().toLowerCase());
        const normalizedRole = (payload?.role || '').trim().toLowerCase();

        if (payload && normalizedAllowedRoles.includes(normalizedRole)) {
          return true;
        }

        this.router.navigate(['/auth/login']);
        return false;
      })
    );
  }
}
