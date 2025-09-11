import { Chart, DoughnutController, BarController, ArcElement, BarElement, CategoryScale, LinearScale, Legend, Tooltip } from 'chart.js';

Chart.register(
  DoughnutController,
  BarController,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip
);

import { enableProdMode } from '@angular/core';
import { environment } from './app/environments/environment';
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';

if (environment.production) {
  enableProdMode();
}

bootstrapApplication(AppComponent, appConfig)
  .catch(err => console.error(err));

