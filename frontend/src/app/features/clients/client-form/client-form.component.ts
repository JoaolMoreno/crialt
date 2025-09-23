import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ClientService } from '../../../core/services/client.service';
import { ActivatedRoute, Router } from '@angular/router';
import { SharedModule } from '../../../shared/shared.module';
import { ViaCepService, ViaCepResponse } from '../../../shared/services/via-cep.service';
import { cpfValidator, cnpjValidator } from '../../../shared/utils/validators';
import { debounceTime, distinctUntilChanged, filter } from 'rxjs/operators';
import { NotificationService } from '../../../shared/notification.service';

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
  private readonly notification = inject(NotificationService);

  form!: FormGroup;
  loading = false;
  error = '';
  isEdit = false;
  clientId: string | null = null;
  cepLoading = false;
  cepError = '';

  documents: File[] = [];
  generatedPassword: string = '';
  showChangePassword = false;
  newPassword = '';

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

  async onResetPassword(): Promise<void> {
    if (!this.isEdit || !this.clientId) {
      this.notification.error('Só é possível redefinir senha ao editar um cliente existente.');
      return;
    }
    this.loading = true;
    this.clientService.resetPassword(this.clientId).subscribe({
      next: (res) => {
        this.loading = false;
        this.generatedPassword = res?.new_password || '';
        if (this.generatedPassword) {
          this.notification.success('Nova senha do cliente: ' + this.generatedPassword);
        } else {
          this.notification.error('Senha redefinida, mas não foi possível obter a nova senha.');
        }
      },
      error: (err) => {
        this.loading = false;
        this.notification.error('Erro ao redefinir senha: ' + (err?.error?.detail || err.message || err));
      }
    });
  }

  onShowChangePassword(): void {
    this.showChangePassword = true;
    this.newPassword = '';
  }

  onCancelChangePassword(): void {
    this.showChangePassword = false;
    this.newPassword = '';
  }

  onConfirmChangePassword(): void {
    if (!this.newPassword || !this.clientId) {
      this.notification.error('Digite a nova senha.');
      return;
    }
    this.loading = true;
    this.clientService.setPassword(this.clientId, this.newPassword).subscribe({
      next: () => {
        this.loading = false;
        this.notification.success('Senha alterada com sucesso!');
        this.showChangePassword = false;
        this.newPassword = '';
      },
      error: (err: any) => {
        this.loading = false;
        this.notification.error('Erro ao alterar senha: ' + (err?.error?.detail || err.message || err));
      }
    });
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.notification.error('Formulário inválido.');
      return;
    }
    this.loading = true;
    this.error = '';
    const data = this.form.value;
    if (this.isEdit && this.clientId) {
      this.clientService.updateClient(this.clientId, data).subscribe({
        next: () => {
          this.notification.success('Cliente atualizado com sucesso!');
          this.router.navigate(['/clients']);
        },
        error: (err) => {
          this.notification.error(err);
          this.loading = false;
        }
      });
    } else {
      this.clientService.createClient(data).subscribe({
        next: () => {
          this.notification.success('Cliente criado com sucesso!');
          this.router.navigate(['/clients']);
        },
        error: (err) => {
          this.notification.error(err);
          this.loading = false;
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
