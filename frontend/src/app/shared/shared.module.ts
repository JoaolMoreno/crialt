import { NgModule } from '@angular/core';
import { CommonModule, NgIf, NgForOf } from '@angular/common';
import { RouterOutlet, RouterLink } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LoadingSpinnerComponent } from './components/loading-spinner/loading-spinner.component';
import { BaseChartDirective } from 'ng2-charts';
import { CeilPipe } from 'src/app/shared/utils/ceil.pipe';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ClientTimezoneDatePipe } from './pipes/client-timezone-date.pipe';
import {MatCheckbox} from "@angular/material/checkbox";
import {MatProgressBarModule} from "@angular/material/progress-bar";
import {MatCardModule} from "@angular/material/card";

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
    FormsModule,
    MatButtonModule,
    MatIconModule,
    ClientTimezoneDatePipe,
    MatCheckbox,
    MatProgressBarModule,
    MatCardModule,
  ],
  declarations: [],
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
    CeilPipe,
    MatButtonModule,
    MatIconModule,
    ClientTimezoneDatePipe,
    MatCheckbox,
    MatProgressBarModule,
    MatCardModule,
  ]
})
export class SharedModule {}
