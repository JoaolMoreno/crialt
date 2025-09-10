import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ClientService } from '../../../core/services/client.service';
import { ActivatedRoute, Router } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';

import { ViaCepService, ViaCepResponse } from '../../../shared/services/via-cep.service';
import { cpfValidator, cnpjValidator } from '../../../shared/utils/validators';
import {LoadingSpinnerComponent} from "../../../shared/components/loading-spinner/loading-spinner.component";
import {NgIf} from "@angular/common";

@Component({
  selector: 'app-client-form',
  standalone: true,
  templateUrl: './client-form.component.html',
  styleUrls: ['./client-form.component.scss'],
    imports: [ReactiveFormsModule, LoadingSpinnerComponent, NgIf]
})
export class ClientFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly clientService = inject(ClientService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly viaCepService = inject(ViaCepService);

  form!: FormGroup;
  loading = false;
  error = '';
  isEdit = false;
  clientId: string | null = null;
  cepLoading = false;
  cepError = '';

  ngOnInit(): void {
    this.clientId = this.route.snapshot.paramMap.get('id');
    this.isEdit = !!this.clientId;
    this.form = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      document: ['', [Validators.required]],
      document_type: ['cpf', [Validators.required]],
      rg_ie: [''],
      birth_date: [''],
      email: ['', [Validators.required, Validators.email]],
      secondary_email: [''],
      phone: ['', [Validators.required]],
      mobile: [''],
      whatsapp: [''],
      address: this.fb.group({
        street: ['', Validators.required],
        number: ['', Validators.required],
        complement: [''],
        neighborhood: ['', Validators.required],
        city: ['', Validators.required],
        state: ['', Validators.required],
        zip_code: ['', Validators.required]
      }),
      notes: [''],
      is_active: [true],
      first_access: [true]
    });
    if (this.isEdit) {
      this.loadClient();
    }
    this.form.get('address.zip_code')?.valueChanges.subscribe((cep: string) => {
      if (cep && cep.length === 8) {
        this.onBuscarCep(cep);
      }
    });
  }

  loadClient(): void {
    this.loading = true;
    this.clientService.getClientById(this.clientId!).subscribe({
      next: (client) => {
        this.form.patchValue(client);
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Erro ao carregar cliente.';
      }
    });
  }

  onBuscarCep(cep: string): void {
    this.cepLoading = true;
    this.cepError = '';
    this.viaCepService.buscarCep(cep).subscribe((res: ViaCepResponse | null) => {
      this.cepLoading = false;
      if (!res || res.erro) {
        this.cepError = 'CEP não encontrado ou inválido.';
        return;
      }
      this.form.patchValue({
        address: {
          street: res.logradouro,
          complement: res.complemento,
          neighborhood: res.bairro,
          city: res.localidade,
          state: res.uf
        }
      });
    });
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.loading = true;
    this.error = '';
    const clientData = this.form.value;
    if (clientData.document_type === 'cpf') {
      if (!cpfValidator(clientData.document)) {
        this.error = 'CPF inválido.';
        this.loading = false;
        return;
      }
    } else {
      if (!cnpjValidator(clientData.document)) {
        this.error = 'CNPJ inválido.';
        this.loading = false;
        return;
      }
    }
    if (this.isEdit) {
      this.clientService.updateClient(this.clientId!, clientData).subscribe({
        next: () => {
          this.loading = false;
          this.router.navigate(['/clients']);
        },
        error: () => {
          this.loading = false;
          this.error = 'Erro ao atualizar cliente.';
        }
      });
    } else {
      this.clientService.createClient(clientData).subscribe({
        next: () => {
          this.loading = false;
          this.router.navigate(['/clients']);
        },
        error: () => {
          this.loading = false;
          this.error = 'Erro ao cadastrar cliente.';
        }
      });
    }
  }
}
