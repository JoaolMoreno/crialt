import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface ViaCepResponse {
  cep: string;
  logradouro: string;
  complemento: string;
  bairro: string;
  localidade: string;
  uf: string;
  erro?: boolean;
}

@Injectable({ providedIn: 'root' })
export class ViaCepService {
  constructor(private http: HttpClient) {}

  buscarCep(cep: string): Observable<ViaCepResponse | null> {
    cep = cep.replace(/\D/g, '');
    if (cep.length !== 8) return of(null);
    return this.http.get<ViaCepResponse>(`https://viacep.com.br/ws/${cep}/json/`).pipe(
      catchError(() => of(null))
    );
  }
}

