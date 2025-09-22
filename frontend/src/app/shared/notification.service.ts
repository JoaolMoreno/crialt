import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root',
})
export class NotificationService {
  constructor(private snackBar: MatSnackBar) {}

  success(message: string, duration: number = 3000) {
    this.snackBar.open(message, 'Fechar', {
      duration,
      panelClass: ['snackbar-success'],
      horizontalPosition: 'center',
      verticalPosition: 'top',
    });
  }

  info(message: string, duration: number = 3000) {
    this.snackBar.open(message, 'Fechar', {
      duration,
      panelClass: ['snackbar-info'],
      horizontalPosition: 'center',
      verticalPosition: 'top',
    });
  }

  error(error: any, duration: number = 5000) {
    console.error(error);
    let message = 'Ocorreu um erro.';
    if (error) {
      if (typeof error === 'string') {
        message = error;
      } else if (error.detail) {
        message = error.detail;
      } else if (error.error.detail){
        message = error.error.detail;
      } else if (error.message) {
        message = error.message;
      }
    }
    this.snackBar.open(message, 'Fechar', {
      duration,
      panelClass: ['snackbar-error'],
      horizontalPosition: 'center',
      verticalPosition: 'top',
    });
  }
}

