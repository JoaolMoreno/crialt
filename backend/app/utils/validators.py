import re
import requests
from typing import Optional

# CPF/CNPJ
def validate_cpf(cpf: str) -> bool:
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i+1) - num) for num in range(0, i)))
        check = ((value * 10) % 11) % 10
        if check != int(cpf[i]):
            return False
    return True

def validate_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14:
        return False
    weight = [5,4,3,2,9,8,7,6,5,4,3,2]
    for i in range(12, 14):
        value = sum(int(cnpj[num]) * weight[num] for num in range(0, i))
        check = ((value * 10) % 11) % 10
        if check != int(cnpj[i]):
            return False
        weight.insert(0, 6 if i == 12 else 5)
    return True

# Email
def validate_email(email: str) -> bool:
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

# Telefone
def validate_phone(phone: str) -> bool:
    return re.match(r"^\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}$", phone) is not None

# CEP (ViaCEP)
def get_address_by_cep(cep: str) -> Optional[dict]:
    cep = re.sub(r'[^0-9]', '', cep)
    if len(cep) != 8:
        return None
    try:
        resp = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if resp.status_code == 200:
            data = resp.json()
            if "erro" not in data:
                return data
    except Exception:
        pass
    return None

# Datas
def validate_dates(start, end) -> bool:
    return end > start

