import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
    private readonly http = inject(HttpClient);

    get<T>(url: string, params?: Record<string, any>): Observable<T> {
        return this.http.get<T>(url, { params, withCredentials: true });
    }

    post<T>(url: string, body: any, options?: { observe?: 'body' } & any): Observable<T>;
    post<T>(url: string, body: any, options: { observe: 'events' } & any): Observable<HttpEvent<T>>;
    post<T>(url: string, body: any, options?: any): Observable<any> {
        return this.http.post(url, body, { ...options, withCredentials: true });
    }

    put<T>(url: string, body: any, options?: { observe?: 'body' } & any): Observable<T>;
    put<T>(url: string, body: any, options: { observe: 'events' } & any): Observable<HttpEvent<T>>;
    put<T>(url: string, body: any, options?: any): Observable<any> {
        return this.http.put(url, body, { ...options, withCredentials: true });
    }

    patch<T>(url: string, body: any, options?: { observe?: 'body' } & any): Observable<T>;
    patch<T>(url: string, body: any, options: { observe: 'events' } & any): Observable<HttpEvent<T>>;
    patch<T>(url: string, body: any, options?: any): Observable<any> {
        return this.http.patch(url, body, { ...options, withCredentials: true });
    }

    delete<T>(url: string, options?: { observe?: 'body' } & any): Observable<T>;
    delete<T>(url: string, options: { observe: 'events' } & any): Observable<HttpEvent<T>>;
    delete<T>(url: string, options?: any): Observable<any> {
        return this.http.delete(url, { ...options, withCredentials: true });
    }
}
