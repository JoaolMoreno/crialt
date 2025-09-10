// Validador de CPF
export function cpfValidator(cpf: string): boolean {
  cpf = cpf.replace(/[\D]/g, '');
  if (cpf.length !== 11 || /^([0-9])\1+$/.test(cpf)) return false;
  let sum = 0;
  for (let i = 0; i < 9; i++) sum += Number(cpf.charAt(i)) * (10 - i);
  let firstCheck = 11 - (sum % 11);
  if (firstCheck > 9) firstCheck = 0;
  if (firstCheck !== Number(cpf.charAt(9))) return false;
  sum = 0;
  for (let i = 0; i < 10; i++) sum += Number(cpf.charAt(i)) * (11 - i);
  let secondCheck = 11 - (sum % 11);
  if (secondCheck > 9) secondCheck = 0;
  return secondCheck === Number(cpf.charAt(10));
}

// Validador de CNPJ
export function cnpjValidator(cnpj: string): boolean {
  cnpj = cnpj.replace(/[\D]/g, '');
  if (cnpj.length !== 14 || /^([0-9])\1+$/.test(cnpj)) return false;
  let length = cnpj.length - 2;
  let numbers = cnpj.substring(0, length);
  let digits = cnpj.substring(length);
  let sum = 0;
  let pos = length - 7;
  for (let i = length; i >= 1; i--) {
    sum += Number(numbers.charAt(length - i)) * pos--;
    if (pos < 2) pos = 9;
  }
  let firstCheck = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  if (firstCheck !== Number(digits.charAt(0))) return false;
  length++;
  numbers = cnpj.substring(0, length);
  sum = 0;
  pos = length - 7;
  for (let i = length; i >= 1; i--) {
    sum += Number(numbers.charAt(length - i)) * pos--;
    if (pos < 2) pos = 9;
  }
  let secondCheck = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  return secondCheck === Number(digits.charAt(1));
}

