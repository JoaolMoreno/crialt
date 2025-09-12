from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..models import Client, Project, Stage
from ..api.dependencies import get_db

router = APIRouter()

@router.get("")
def get_dashboard(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_6_months = [(now.replace(day=1) - timedelta(days=30*i)) for i in range(6)]
    months = [(d.month, d.year) for d in reversed(last_6_months)]

    # Total de clientes ativos
    total_clients = db.query(func.count()).select_from(Client).filter(Client.is_active == True).scalar()

    # Projetos ativos
    active_projects = db.query(func.count()).select_from(Project).filter(Project.status == "active").scalar()

    # Projetos finalizados no mês atual
    completed_projects_this_month = db.query(func.count()).select_from(Project).filter(
        Project.status == "completed",
        Project.actual_end_date >= first_day_month,
        Project.actual_end_date < now.replace(day=now.day+1)
    ).scalar()

    # Receita do mês atual
    month_revenue = db.query(func.coalesce(func.sum(Project.total_value), 0)).filter(
        Project.status == "completed",
        Project.actual_end_date >= first_day_month,
        Project.actual_end_date < now.replace(day=now.day+1)
    ).scalar()

    # 5 projetos mais recentes
    recent_projects = db.query(Project).order_by(Project.created_at.desc()).limit(5).all()
    recent_projects_serialized = [
        {
            "id": p.id,
            "name": p.name,
            "description": getattr(p, "description", None),
            "total_value": p.total_value,
            "currency": p.currency,
            "start_date": p.start_date,
            "estimated_end_date": p.estimated_end_date,
            "actual_end_date": getattr(p, "actual_end_date", None),
            "status": p.status,
            "work_address": getattr(p, "work_address", None),
            "scope": getattr(p, "scope", None),
            "notes": getattr(p, "notes", None),
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "created_by_id": p.created_by_id,
            "client_name": p.clients[0].name if p.clients else None
        } for p in recent_projects
    ]

    # Contagem de projetos por status
    status_list = ["active", "paused", "completed", "cancelled", "draft"]
    projects_status_counts = {}
    for status in status_list:
        count = db.query(func.count()).select_from(Project).filter(Project.status == status).scalar()
        projects_status_counts[status] = count

    # Receita dos últimos 6 meses
    revenue_by_month = []
    for month, year in months:
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year+1, 1, 1)
        else:
            end = datetime(year, month+1, 1)
        value = db.query(func.coalesce(func.sum(Project.total_value), 0)).filter(
            Project.status == "completed",
            Project.actual_end_date >= start,
            Project.actual_end_date < end
        ).scalar()
        revenue_by_month.append({
            "month": start.strftime("%b"),
            "year": str(start.year)[-2:],
            "value": float(value) if value else 0
        })

    # Etapas próximas do prazo (próximos 7 dias, não completadas)
    near_deadline = now + timedelta(days=7)
    stages_near_deadline = db.query(func.count()).select_from(Stage).filter(
        Stage.status != "completed",
        Stage.planned_end_date >= now.date(),
        Stage.planned_end_date <= near_deadline.date()
    ).scalar()

    return {
        "total_clients": total_clients,
        "active_projects": active_projects,
        "completed_projects_this_month": completed_projects_this_month,
        "month_revenue": float(month_revenue) if month_revenue else 0,
        "recent_projects": recent_projects_serialized,
        "projects_status_counts": projects_status_counts,
        "revenue_by_month": revenue_by_month,
        "stages_near_deadline": stages_near_deadline
    }
