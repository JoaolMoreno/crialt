import { Component, inject, OnInit } from '@angular/core';
import { ProjectService } from '../../core/services/project.service';
import { ClientService } from '../../core/services/client.service';
import { DashboardService, DashboardData } from '../../core/services/dashboard.service';
import { Project } from '../../core/models/project.model';
import { ChartConfiguration } from 'chart.js';
import { SharedModule } from '../../shared/shared.module';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
  imports: [SharedModule]
})
export class DashboardComponent implements OnInit {
  private readonly projectService = inject(ProjectService);
  private readonly clientService = inject(ClientService);
  private readonly dashboardService = inject(DashboardService);

  loading = false;
  error = '';

  // Estatísticas
  totalClients = 0;
  activeProjects = 0;
  completedProjectsThisMonth = 0;
  monthRevenue = 0;
  stagesNearDeadline = 0;

  // Projetos recentes
  recentProjects: Project[] = [];

  // Gráficos
  projectsStatusChartData: ChartConfiguration<'doughnut'> = {
    type: 'doughnut',
    data: {
      labels: ['Em andamento', 'Pausado', 'Concluído', 'Cancelado', 'Rascunho'],
      datasets: [{
        data: [0, 0, 0, 0, 0],
        backgroundColor: ['#708090', '#F5F5F5', '#212121', '#d32f2f', '#666666'],
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  };

  revenueChartData: ChartConfiguration<'bar'> = {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{
        label: 'Receita Mensal',
        data: [],
        backgroundColor: '#708090',
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      }
    }
  };

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.loading = true;
    this.error = '';
    this.dashboardService.getDashboardData().subscribe({
      next: (data: DashboardData) => {
        this.totalClients = data.total_clients;
        this.activeProjects = data.active_projects;
        this.completedProjectsThisMonth = data.completed_projects_this_month;
        this.monthRevenue = data.month_revenue;
        this.recentProjects = data.recent_projects;
        this.stagesNearDeadline = data.stages_near_deadline;
        this.projectsStatusChartData.data.datasets[0].data = [
          data.projects_status_counts.active || 0,
          data.projects_status_counts.paused || 0,
          data.projects_status_counts.completed || 0,
          data.projects_status_counts.cancelled || 0,
          data.projects_status_counts.draft || 0
        ];
        this.revenueChartData.data.labels = data.revenue_by_month.map(m => `${m.month}/${m.year}`);
        this.revenueChartData.data.datasets[0].data = data.revenue_by_month.map(m => m.value);
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Erro ao buscar dados do dashboard.';
      }
    });
  }
}
