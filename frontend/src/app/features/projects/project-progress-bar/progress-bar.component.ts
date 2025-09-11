import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-progress-bar',
  templateUrl: './progress-bar.component.html',
  styleUrls: ['./progress-bar.component.scss'],
  standalone: true
})
export class ProgressBarComponent {
  @Input() progress: number = 0; // 0 a 100
}

