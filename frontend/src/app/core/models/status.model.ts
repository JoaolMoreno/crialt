export type ProjectStatus =
  | 'draft'
  | 'active'
  | 'paused'
  | 'completed'
  | 'cancelled';

export type StageStatus =
  | 'pending'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'on_hold';

export type StatusType = ProjectStatus | StageStatus;

export interface StatusBadge {
  value: StatusType;
  label: string; // Nome em português
  color: string; // Classe CSS ou cor
}

export const STATUS_BADGES: StatusBadge[] = [
  { value: 'draft', label: 'Rascunho', color: 'gray' },
  { value: 'active', label: 'Ativo', color: 'blue' },
  { value: 'paused', label: 'Pausado', color: 'orange' },
  { value: 'completed', label: 'Concluído', color: 'green' },
  { value: 'cancelled', label: 'Cancelado', color: 'red' },
  { value: 'pending', label: 'Pendente', color: 'gray' },
  { value: 'in_progress', label: 'Em andamento', color: 'blue' },
  { value: 'on_hold', label: 'Em espera', color: 'orange' },
];

export function getStatusBadge(status: string): StatusBadge {
  const badge = STATUS_BADGES.find(b => b.value === status);
  if (badge) return badge;
  return {
    value: status as StatusType,
    label: status,
    color: 'gray',
  };
}
