import { Component, inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-project-form',
  standalone: true,
  templateUrl: './project-form.component.html',
  styleUrls: ['./project-form.component.scss']
})
export class ProjectFormComponent {
  isEdit = false;
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  constructor() {
    const id = this.route.snapshot.paramMap.get('id');
    this.isEdit = !!id;
  }

  onBack(): void {
    this.router.navigate(['/projects']);
  }
}
