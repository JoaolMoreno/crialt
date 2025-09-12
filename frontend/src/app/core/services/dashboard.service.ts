import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface DashboardData {
  total_clients: number;
  active_projects: number;
  completed_projects_this_month: number;
  month_revenue: number;
  recent_projects: any[];
  projects_status_counts: Record<string, number>;
  revenue_by_month: { month: string; year: string; value: number }[];
  stages_near_deadline: number;
}

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/dashboard`;

  getDashboardData(): Observable<DashboardData> {
    return this.http.get<DashboardData>(this.apiUrl, { withCredentials: true });
  }
}

