import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, catchError, of } from 'rxjs';
import { map } from 'rxjs/operators';
import { User } from '../models/user.model';
import { Client } from '../models/client.model';
import { environment } from '../../environments/environment';

type UserOrClient = User | Client;

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/auth`;
  private userSubject = new BehaviorSubject<UserOrClient | null>(null);
  public user$ = this.userSubject.asObservable();
  private isClient = false;

  constructor() {
    const storedIsClient = localStorage.getItem('isClient');
    this.isClient = storedIsClient === 'true';
  }

  /**
   * Login para usuário (admin, arquiteto, assistente) ou cliente.
   * Envia dados como application/x-www-form-urlencoded (form-data), compatível com OAuth2PasswordRequestForm do backend.
   */
  login(params: { username: string; password: string }): Observable<any> {
    const form = new URLSearchParams();
    form.append('username', params.username);
    form.append('password', params.password);
    return this.http.post<any>(`${this.apiUrl}/login`, form.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      withCredentials: true
    }).pipe(
      catchError(err => {
        console.error('[AuthService] login: erro ao fazer login', err);
        return of(err);
      }),
    );
  }

  /**
   * Busca o usuário ou cliente logado, dependendo do tipo de login.
   */
  fetchCurrentUser(): Observable<UserOrClient | null> {
    return new Observable<UserOrClient | null>(observer => {
      const endpoint = this.isClient ? '/clients/me' : '/users/me';
      const fullUrl = `${environment.apiUrl}${endpoint}`;

      this.http.get<UserOrClient>(fullUrl, { withCredentials: true }).subscribe({
        next: (data) => {
          this.userSubject.next(data);
          observer.next(data);
        },
        error: (err) => {
          this.userSubject.next(null);
          observer.next(null);
        },
        complete: () => {
          observer.complete();
        }
      });
    });
  }

  /**
   * Chamada para ser feita após login, para armazenar o tipo correto e atualizar o estado.
   */
  handleLoginResponse(response: any): void {
    if (response && response.client) {
      this.isClient = true;
      localStorage.setItem('isClient', 'true');
      this.userSubject.next(response.client);
    } else if (response && response.user) {
      this.isClient = false;
      localStorage.setItem('isClient', 'false');
      this.userSubject.next(response.user);
    } else {
      this.isClient = false;
      localStorage.setItem('isClient', 'false');
      this.userSubject.next(null);
    }
  }

  logout(): void {
    this.http.post(`${this.apiUrl}/logout`, {}).subscribe({
      complete: () => {
        this.userSubject.next(null);
        this.isClient = false;
        localStorage.setItem('isClient', 'false');
      },
      error: (err) => {
        this.userSubject.next(null);
        this.isClient = false;
        localStorage.removeItem('isClient');
      }
    });
  }

  checkToken(): Observable<{ role: string; name: string; sub: string } | null> {
    return this.http.get<{ role: string; name: string; sub: string }>(`${this.apiUrl}/check-token`, { withCredentials: true })
      .pipe(
        map(result => {
          return result;
        }),
        catchError(err => {
          this.logout();
          return of(null);
        })
      );
  }

  isClientLogged(): boolean {
    return this.isClient;
  }
}
