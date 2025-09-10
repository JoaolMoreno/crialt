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

  documents: File[] = [];
  generatedPassword: string = '';
  isAdmin: boolean = false;

  ngOnInit(): void {
    this.clientId = this.route.snapshot.paramMap.get('id');
    this.isEdit = !!this.clientId;
    const draft = localStorage.getItem('clientFormDraft');
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
      first_access: [true],
      documents: [[]],
    });
    if (draft && !this.isEdit) {
      this.form.patchValue(JSON.parse(draft));
    }
    if (this.isEdit) {
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
    this.form.valueChanges.subscribe(val => {
      if (!this.isEdit) {
        localStorage.setItem('clientFormDraft', JSON.stringify(val));
      }
    });
  }

  onBuscarCep(): void {
    const cep = this.form.get('address.zip_code')?.value;
    if (!cep || cep.length < 8) {
      this.cepError = 'Informe um CEP válido.';
      return;
    }
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

  onResetPassword(): void {
    // Mock: redefinir senha
    this.generatedPassword = Math.random().toString(36).slice(-8);
    alert('Senha redefinida: ' + this.generatedPassword);
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    const data = { ...this.form.value };

    this.clientService.updateClient(data, this.form.value.documents).subscribe({
      next: () => {
        this.loading = false;
        localStorage.removeItem('clientFormDraft');
        this.router.navigate(['/clients']);
      },
      error: () => {
        this.loading = false;
        this.error = 'Erro ao salvar cliente.';
      }
    });
  }

  onBack(): void {
    if (this.isEdit) {
      this.router.navigate(['/clients']);
    } else {
      this.router.navigate(['/clients']);
    }
  }
}
