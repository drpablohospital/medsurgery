from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Visita, Ticket, Usuario, Hospital, Material
from datetime import datetime, date
from sqlalchemy import extract

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    hoy = date.today()
    
    if current_user.es_admin():
        # Dashboard para admin - resumen global
        # Estadísticas de visitas
        visitas_total = Visita.query.count()
        visitas_hoy = Visita.query.filter(Visita.fecha == hoy).count()
        visitas_pendientes_count = Visita.query.filter(
            Visita.fecha >= hoy,
            Visita.estado.in_(['programada', 'confirmada'])
        ).count()
        
        # Promotores y hospitales
        total_promotores = Usuario.query.filter_by(tipo='promotor', activo=True).count()
        total_hospitales = Hospital.query.filter_by(activo=True).count()
        total_materiales = Material.query.filter_by(activo=True).count()
        
        # Tickets
        tickets_pendientes = Ticket.query.filter_by(estado='pendiente').count()
        tickets_aprobados = Ticket.query.filter_by(estado='aprobado').count()
        tickets_pagados = Ticket.query.filter_by(estado='pagado').count()
        tickets_cobrados = Ticket.query.filter_by(estado='cobrado').count()
        
        # Montos
        tickets_pagados_list = Ticket.query.filter_by(estado='pagado').all()
        monto_pagado = sum(float(t.monto) for t in tickets_pagados_list) if tickets_pagados_list else 0
        
        tickets_pendientes_list = Ticket.query.filter_by(estado='pendiente').all()
        monto_pendiente = sum(float(t.monto) for t in tickets_pendientes_list) if tickets_pendientes_list else 0
        
        tickets_aprobados_list = Ticket.query.filter_by(estado='aprobado').all()
        monto_aprobado = sum(float(t.monto) for t in tickets_aprobados_list) if tickets_aprobados_list else 0
        
        # Calcular ganancias: ingresos (materiales vendidos) - gastos (costo de visitas)
        tickets_cobrados_list = Ticket.query.filter_by(estado='cobrado').all()
        total_ingresos = 0
        total_gastos = 0
        
        for t in tickets_cobrados_list:
            if t.materiales_vendidos:
                for mat in t.materiales_vendidos:
                    total_ingresos += float(mat.get('precio_venta', 0)) * int(mat.get('cantidad', 1))
            if t.visita:
                total_gastos += float(t.visita.costo_visita or 0)
        
        ganancia_neta = total_ingresos - total_gastos
        
        # Promotores activos
        promotores_activos = Usuario.query.filter_by(tipo='promotor', activo=True).count()
        
        # Visitas recientes
        ultimas_visitas = Visita.query.order_by(Visita.created_at.desc()).limit(10).all()
        ultimos_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()
        
        return render_template('admin/dashboard.html',
                             total_promotores=total_promotores,
                             total_hospitales=total_hospitales,
                             total_materiales=total_materiales,
                             visitas_total=visitas_total,
                             visitas_hoy=visitas_hoy,
                             visitas_pendientes=visitas_pendientes_count,
                             tickets_pendientes=tickets_pendientes,
                             tickets_aprobados=tickets_aprobados,
                             tickets_pagados=tickets_pagados,
                             tickets_cobrados=tickets_cobrados,
                             total_ingresos=total_ingresos,
                             total_gastos=total_gastos,
                             ganancia_neta=ganancia_neta,
                             monto_pagado=monto_pagado,
                             monto_pendiente=monto_pendiente,
                             monto_aprobado=monto_aprobado,
                             promotores_activos=promotores_activos,
                             ultimas_visitas=ultimas_visitas,
                             ultimos_tickets=ultimos_tickets)
    
    # Dashboard para promotores
    hoy = date.today()
    
    # Próximas visitas
    proximas_visitas = Visita.query.filter(
        Visita.usuario_id == current_user.id,
        Visita.fecha >= hoy,
        Visita.estado.in_(['programada', 'confirmada'])
    ).order_by(Visita.fecha, Visita.hora_inicio).limit(5).all()
    
    # Total de visitas este mes
    visitas_mes = Visita.query.filter(
        Visita.usuario_id == current_user.id,
        extract('month', Visita.fecha) == hoy.month,
        extract('year', Visita.fecha) == hoy.year,
        Visita.estado == 'realizada'
    ).count()
    
    # Tickets pendientes de pago
    tickets_pendientes = Ticket.query.filter(
        Ticket.usuario_id == current_user.id,
        Ticket.estado == 'pendiente'
    ).order_by(Ticket.created_at.desc()).limit(5).all()
    
    # Total de tickets pagados
    total_cobrado = Ticket.query.filter(
        Ticket.usuario_id == current_user.id,
        Ticket.estado == 'pagado'
    ).all()
    
    total_ganado = sum(float(t.monto) for t in total_cobrado) if total_cobrado else 0
    
    # Venta de materiales (ingresos para la organizacion)
    total_venta_materiales = 0
    for t in total_cobrado:
        if t.materiales_vendidos:
            for mat in t.materiales_vendidos:
                total_venta_materiales += float(mat.get("precio_venta", 0)) * mat.get("cantidad", 1)
    
    # Rentabilidad = venta de materiales / honorarios pagados
    rentabilidad = (total_venta_materiales / total_ganado * 100) if total_ganado > 0 else 0
    
    # Ofertas disponibles
    ofertas_disponibles = Visita.query.filter(
        Visita.modo_asignacion == 'oferta',
        Visita.usuario_id.is_(None),
        Visita.estado == 'programada',
        Visita.fecha >= hoy
    ).count()
    
    return render_template('dashboard.html',
                         proximas_visitas=proximas_visitas,
                         visitas_mes=visitas_mes,
                         tickets_pendientes=tickets_pendientes,
                         total_ganado=total_ganado,
                         ofertas_disponibles=ofertas_disponibles,
                         total_venta_materiales=total_venta_materiales,
                         rentabilidad=rentabilidad)
