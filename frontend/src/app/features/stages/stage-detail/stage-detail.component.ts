import { Component } from '@angular/core';
import { SharedModule } from '../../../shared/shared.module';

@Component({
  selector: 'app-stage-detail',
  standalone: true,
  templateUrl: './stage-detail.component.html',
  styleUrls: ['./stage-detail.component.scss'],
  imports: [SharedModule]
})
export class StageDetailComponent {}
