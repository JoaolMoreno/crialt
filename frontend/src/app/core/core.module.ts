import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

// Core services, guards, interceptors não precisam ser declarados, apenas providos
@NgModule({
    imports: [CommonModule],
    providers: []
})
export class CoreModule {}