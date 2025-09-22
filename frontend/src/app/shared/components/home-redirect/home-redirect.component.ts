import { Component, ViewContainerRef, ComponentRef, OnInit } from '@angular/core';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-home-redirect',
  template: '',
})
export class HomeRedirectComponent implements OnInit {
  private componentRef?: ComponentRef<any>;

  constructor(
    private viewContainerRef: ViewContainerRef,
    private authService: AuthService
  ) {}

  async ngOnInit() {
    this.viewContainerRef.clear();
    if (this.authService.isClientLogged()) {
      const { ClientHomeComponent } = await import('src/app/features/clients/client-home/client-home.component');
      this.componentRef = this.viewContainerRef.createComponent(ClientHomeComponent);
    } else {
      const { DashboardComponent } = await import('src/app/features/dashboard/dashboard.component');
      this.componentRef = this.viewContainerRef.createComponent(DashboardComponent);
    }
  }
}
