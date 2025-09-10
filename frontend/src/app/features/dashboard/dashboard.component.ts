import { Component, inject, OnInit } from '@angular/core';
import { ProjectService } from '../../core/services/project.service';
import { ClientService } from '../../core/services/client.service';
import { Project } from '../../core/models/project.model';
import { ChartConfiguration, ChartType } from 'chart.js';
import { CommonModule } from '@angular/common';
import {LoadingSpinnerComponent} from "../../shared/components/loading-spinner/loading-spinner.component";
import {BaseChartDirective} from "ng2-charts";

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
    imports: [CommonModule, LoadingSpinnerComponent, BaseChartDirective]
})
export class DashboardComponent implements OnInit {
  private readonly projectService = inject(ProjectService);
  private readonly clientService = inject(ClientService);

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
    this.clientService.getClients().subscribe({
      next: (clients) => {
        this.totalClients = clients.filter(c => c.is_active).length;
        this.projectService.getProjects().subscribe({
          next: (projects) => {
            this.activeProjects = projects.filter(p => p.status === 'active').length;
            const now = new Date();
            this.completedProjectsThisMonth = projects.filter(p => {
              if (!p.actual_end_date) return false;
              const endDate = new Date(p.actual_end_date);
              return endDate.getMonth() === now.getMonth() && endDate.getFullYear() === now.getFullYear();
            }).length;
            this.monthRevenue = projects.filter(p => {
              if (!p.actual_end_date) return false;
              const endDate = new Date(p.actual_end_date);
              return endDate.getMonth() === now.getMonth() && endDate.getFullYear() === now.getFullYear();
            }).reduce((sum, p) => sum + p.total_value, 0);
            this.recentProjects = projects.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()).slice(0, 5);
            // Gráfico de status dos projetos
            const statusCounts = {
              active: 0, paused: 0, completed: 0, cancelled: 0, draft: 0
            };
            projects.forEach(p => {
              if (statusCounts[p.status] !== undefined) statusCounts[p.status]++;
            });
            this.projectsStatusChartData.data.datasets[0].data = [
              statusCounts.active,
              statusCounts.paused,
              statusCounts.completed,
              statusCounts.cancelled,
              statusCounts.draft
            ];
            // Gráfico de receita mensal (últimos 6 meses)
            const months: string[] = [];
            const revenueByMonth: number[] = [];
            for (let i = 5; i >= 0; i--) {
              const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
              months.push(d.toLocaleString('pt-BR', { month: 'short', year: '2-digit' }));
              const monthRevenue = projects.filter(p => {
                if (!p.actual_end_date) return false;
                const endDate = new Date(p.actual_end_date);
                return endDate.getMonth() === d.getMonth() && endDate.getFullYear() === d.getFullYear();
              }).reduce((sum, p) => sum + p.total_value, 0);
              revenueByMonth.push(monthRevenue);
            }
            this.revenueChartData.data.labels = months;
            this.revenueChartData.data.datasets[0].data = revenueByMonth;

            this.loading = false;
          },
          error: () => {
            this.loading = false;
            this.error = 'Erro ao buscar projetos.';
          }
        });
      },
      error: () => {
        this.loading = false;
        this.error = 'Erro ao buscar clientes.';
      }
    });
  }
}
