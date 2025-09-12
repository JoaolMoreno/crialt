import { Component } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import {HeaderComponent} from "../../shared/components/header/header.component";
import {SidebarComponent} from "../../shared/components/sidebar/sidebar.component";

@Component({
    selector: 'app-main-layout',
    templateUrl: './main-layout.component.html',
    styleUrls: ['./main-layout.component.scss'],
    imports: [SharedModule, HeaderComponent, SidebarComponent]
})
export class MainLayoutComponent {}
