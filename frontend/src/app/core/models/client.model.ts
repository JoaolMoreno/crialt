import { Project } from './project.model';
import { File } from './file.model';

export interface Client {
  id: string;
  name: string;
  document: string;
  document_type: 'cpf' | 'cnpj';
  rg_ie?: string;
  birth_date?: string;
  email: string;
  secondary_email?: string;
  phone: string;
  mobile?: string;
  whatsapp?: string;
  password_hash: string;
  first_access: boolean;
  address: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  };
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  projects: Project[];
  documents: File[];
}

