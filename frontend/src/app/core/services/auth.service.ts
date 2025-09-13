import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, catchError, of } from 'rxjs';
import { User } from '../models/user.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/auth`;
  private userSubject = new BehaviorSubject<User | null>(null);
  public user$ = this.userSubject.asObservable();

  /**
   * Login para usuário (admin, arquiteto, assistente) ou cliente.
   * Envia dados como application/x-www-form-urlencoded (form-data), compatível com OAuth2PasswordRequestForm do backend.
   */
  login(params: { username?: string; email?: string; password: string }): Observable<any> {
    const form = new URLSearchParams();
    if (params.username) {
      form.append('username', params.username);
    } else if (params.email) {
      form.append('username', params.email);
    }
    form.append('password', params.password);
    return this.http.post<any>(`${this.apiUrl}/login`, form.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      withCredentials: true
    });
  }

  fetchCurrentUser(): Observable<User | null> {
    return new Observable<User | null>(observer => {
      this.http.get<User>(`${environment.apiUrl}/users/me`, { withCredentials: true }).subscribe({
        next: (user) => {
          this.userSubject.next(user);
          observer.next(user);
        },
        error: () => {
          this.userSubject.next(null);
          observer.next(null);
        },
        complete: () => observer.complete()
      });
    });
  }

  logout(): void {
    this.http.post(`${this.apiUrl}/logout`, {}).subscribe({
      complete: () => {
        this.userSubject.next(null);
      }
    });
  }

  getCurrentUser(): Observable<User | null> {
    return this.user$;
  }

  setCurrentUser(user: User): void {
    this.userSubject.next(user);
  }

  checkToken(): Observable<{ role: string; name: string; sub: string } | null> {
    return this.http.get<{ role: string; name: string; sub: string }>(`${this.apiUrl}/check-token`, { withCredentials: true })
      .pipe(
        catchError(err => {
          this.logout();
          return of(null);
        })
      );
  }
}
