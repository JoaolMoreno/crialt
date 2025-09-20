import { NgModule } from '@angular/core';
import { CommonModule, NgIf, NgForOf } from '@angular/common';
import { RouterOutlet, RouterLink } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LoadingSpinnerComponent } from './components/loading-spinner/loading-spinner.component';
import { BaseChartDirective } from 'ng2-charts';
import { CeilPipe } from 'src/app/shared/utils/ceil.pipe';
import { MatSnackBarModule } from '@angular/material/snack-bar';

@NgModule({
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterOutlet,
    RouterLink,
    NgIf,
    NgForOf,
    BaseChartDirective,
    LoadingSpinnerComponent,
    CeilPipe,
    FormsModule,
    MatSnackBarModule,
  ],
  exports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    RouterOutlet,
    RouterLink,
    NgIf,
    NgForOf,
    BaseChartDirective,
    LoadingSpinnerComponent,
    CeilPipe,
    MatSnackBarModule,
  ]
})
export class SharedModule {}
