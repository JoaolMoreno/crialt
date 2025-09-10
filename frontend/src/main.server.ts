import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { config } from './app/app.config.server';
import { ApplicationRef } from '@angular/core';

export default function bootstrap(): Promise<ApplicationRef> {
    return bootstrapApplication(AppComponent, config);
}
