import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'clientTimezoneDate'
})
export class ClientTimezoneDatePipe implements PipeTransform {
  transform(value: string | Date | number | null | undefined, format: string = 'dd/MM/yyyy HH:mm'): string {
    if (!value) return '';
    let date: Date;
    if (typeof value === 'string') {
      // Tenta converter string para Date, tratando ISO e outros formatos
      date = new Date(value);
    } else {
      date = new Date(value);
    }
    if (isNaN(date.getTime())) return '';
    // Usa Intl.DateTimeFormat para garantir fuso do cliente
    const options: Intl.DateTimeFormatOptions = this.parseFormat(format);
    return new Intl.DateTimeFormat(undefined, options).format(date);
  }

  // Converte string de formato simples para opções do Intl.DateTimeFormat
  private parseFormat(format: string): Intl.DateTimeFormatOptions {
    // Suporte básico para os formatos mais usados
    if (format.includes('yyyy') && format.includes('HH')) {
      return { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
    } else if (format.includes('yyyy')) {
      return { year: 'numeric', month: '2-digit', day: '2-digit' };
    } else if (format.includes('HH')) {
      return { hour: '2-digit', minute: '2-digit' };
    }
    return {};
  }
}

