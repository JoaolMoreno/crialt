// Estrutura base para guard de roles
import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class RoleGuard implements CanActivate {
  constructor(private router: Router) {}
  canActivate(): boolean {
    // Implementar lógica de permissão por role
    return true;
  }
}

