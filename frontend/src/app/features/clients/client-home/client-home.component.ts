import { Component } from '@angular/core';

@Component({
  selector: 'app-client-home',
  template: `
    <div class="client-home">
      <h1>Bem-vindo, Cliente!</h1>
      <p>Esta é a sua página inicial. Aqui você pode acessar seus projetos e informações principais.</p>
    </div>
  `,
  styles: [`
    .client-home {
      padding: 2rem;
      text-align: center;
    }
  `]
})
export class ClientHomeComponent {}

