import { Component } from '@angular/core';
import { SharedModule } from './shared/shared.module';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  imports: [SharedModule]
})
export class AppComponent {
  title = 'Crialt Arquitetura - Painel Administrativo';
}
