import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ClientService } from '../../../core/services/client.service';
import { ActivatedRoute, Router } from '@angular/router';
import { SharedModule } from '../../../shared/shared.module';
import { ViaCepService, ViaCepResponse } from '../../../shared/services/via-cep.service';
import { cpfValidator, cnpjValidator } from '../../../shared/utils/validators';
import { debounceTime, distinctUntilChanged, filter } from 'rxjs/operators';

@Component({
  selector: 'app-client-form',
  standalone: true,
  templateUrl: './client-form.component.html',
  styleUrls: ['./client-form.component.scss'],
    imports: [SharedModule]
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

    // Busca automática de CEP após 3s do término da digitação
    this.form.get('address.zip_code')?.valueChanges
      .pipe(
        debounceTime(3000),
        distinctUntilChanged(),
        filter((cep: string) => !!cep && cep.length === 8)
      )
      .subscribe((cep: string) => {
        this.buscarCepAutomatico(cep);
      });

    // Aplica o validator correto ao campo document conforme o tipo
    this.setDocumentValidator(this.form.get('document_type')?.value);
    this.form.get('document_type')?.valueChanges.subscribe(type => {
      this.setDocumentValidator(type);
      this.form.get('document')?.updateValueAndValidity();
    });
  }

  buscarCepAutomatico(cep: string): void {
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

  setDocumentValidator(type: string) {
    const documentControl = this.form.get('document');
    if (!documentControl) return;
    if (type === 'cpf') {
      documentControl.setValidators([Validators.required, cpfValidator]);
    } else {
      documentControl.setValidators([Validators.required, cnpjValidator]);
    }
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
    if (this.isEdit && this.clientId) {
      this.clientService.updateClient(this.clientId, data).subscribe({
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
    } else {
      this.clientService.createClient(data).subscribe({
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
  }

  onBack(): void {
    if (this.isEdit) {
      this.router.navigate(['/clients']);
    } else {
      this.router.navigate(['/clients']);
    }
  }
}
