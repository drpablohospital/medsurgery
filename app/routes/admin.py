from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Usuario, Hospital, Material, Visita, Ticket
from app.utils.decorators import admin_required
from app.utils.helpers import generar_numero_ticket
from werkzeug.security import generate_password_hash
from datetime import datetime, date
from sqlalchemy import func

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@admin_required
def dashboard():
    # Estadisticas
    total_promotores = Usuario.query.filter_by(tipo='promotor', activo=True).count()
    total_hospitales = Hospital.query.filter_by(activo=True).count()
    total_materiales = Material.query.filter_by(activo=True).count()
    
    # Visitas hoy
    hoy = date.today()
    visitas_hoy = Visita.query.filter(
        Visita.fecha == hoy,
        Visita.estado.notin_(['cancelada', 'no_show'])
    ).count()
    
    # Tickets
    tickets_pendientes = Ticket.query.filter_by(estado='pendiente').count()
    tickets_aprobados = Ticket.query.filter_by(estado='aprobado').count()
    tickets_pagados = Ticket.query.filter_by(estado='pagado').count()
    
    # Montos
    monto_pendiente = db.session.query(func.sum(Ticket.monto)).filter_by(estado='pendiente').scalar() or 0
    monto_pagado = db.session.query(func.sum(Ticket.monto)).filter_by(estado='pagado').scalar() or 0
    monto_aprobado = db.session.query(func.sum(Ticket.monto)).filter_by(estado='aprobado').scalar() or 0
    
    # Ultimas visitas
    ultimas_visitas = Visita.query.order_by(Visita.created_at.desc()).limit(10).all()
    
    # Tickets recientes
    ultimos_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_promotores=total_promotores,
                         total_hospitales=total_hospitales,
                         total_materiales=total_materiales,
                         visitas_hoy=visitas_hoy,
                         tickets_pendientes=tickets_pendientes,
                         tickets_aprobados=tickets_aprobados,
                         tickets_pagados=tickets_pagados,
                         monto_pendiente=float(monto_pendiente),
                         monto_pagado=float(monto_pagado),
                         monto_aprobado=float(monto_aprobado),
                         ultimas_visitas=ultimas_visitas,
                         ultimos_tickets=ultimos_tickets)

# ============================================================
# GESTION DE PROMOTORES (antes usuarios)
# ============================================================

@bp.route('/promotores')
@admin_required
def promotores():
    promotores = Usuario.query.filter_by(tipo='promotor').order_by(Usuario.nombre).all()
    return render_template('admin/promotores.html', promotores=promotores)

@bp.route('/promotores/nuevo', methods=['POST'])
@admin_required
def promotor_nuevo():
    nombre = request.form.get('nombre', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    telefono = request.form.get('telefono', '').strip()
    region_asignada = request.form.get('region_asignada', '').strip()
    
    if not nombre or not email or not password:
        flash('Nombre, email y contraseña son requeridos.', 'warning')
        return redirect(url_for('admin.promotores'))
    
    if len(password) < 6:
        flash('La contraseña debe tener al menos 6 caracteres.', 'warning')
        return redirect(url_for('admin.promotores'))
    
    if Usuario.query.filter_by(email=email).first():
        flash('Este email ya esta registrado.', 'danger')
        return redirect(url_for('admin.promotores'))
    
    user = Usuario(
        nombre=nombre,
        email=email,
        tipo='promotor',
        telefono=telefono,
        region_asignada=region_asignada
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    flash(f'Promotor {nombre} creado correctamente.', 'success')
    return redirect(url_for('admin.promotores'))

@bp.route('/promotores/<int:promotor_id>/editar', methods=['POST'])
@admin_required
def promotor_editar(promotor_id):
    user = Usuario.query.get_or_404(promotor_id)
    
    user.nombre = request.form.get('nombre', user.nombre).strip()
    user.email = request.form.get('email', user.email).strip().lower()
    user.telefono = request.form.get('telefono', user.telefono).strip()
    user.region_asignada = request.form.get('region_asignada', user.region_asignada).strip()
    user.activo = request.form.get('activo') == 'on'
    
    new_pass = request.form.get('nueva_password', '')
    if new_pass and len(new_pass) >= 6:
        user.set_password(new_pass)
        flash(f'Contrasena de {user.nombre} actualizada.', 'info')
    
    db.session.commit()
    flash(f'Promotor {user.nombre} actualizado.', 'success')
    return redirect(url_for('admin.promotores'))

# ============================================================
# GESTION DE HOSPITALES (antes salas)
# ============================================================

@bp.route('/hospitales')
@admin_required
def hospitales():
    hospitales = Hospital.query.order_by(Hospital.nombre).all()
    return render_template('admin/hospitales.html', hospitales=hospitales)

@bp.route('/hospitales/nuevo', methods=['POST'])
@admin_required
def hospital_nuevo():
    nombre = request.form.get('nombre', '').strip()
    direccion = request.form.get('direccion', '').strip()
    ciudad = request.form.get('ciudad', 'Queretaro').strip()
    telefono = request.form.get('telefono', '').strip()
    contacto_nombre = request.form.get('contacto_nombre', '').strip()
    contacto_email = request.form.get('contacto_email', '').strip()
    contacto_telefono = request.form.get('contacto_telefono', '').strip()
    tipo = request.form.get('tipo', 'privado').strip()
    notas = request.form.get('notas', '').strip()
    
    if not nombre:
        flash('El nombre del hospital es requerido.', 'warning')
        return redirect(url_for('admin.hospitales'))
    
    hospital = Hospital(
        nombre=nombre,
        direccion=direccion,
        ciudad=ciudad,
        telefono=telefono,
        contacto_nombre=contacto_nombre,
        contacto_email=contacto_email,
        contacto_telefono=contacto_telefono,
        tipo=tipo,
        notas=notas
    )
    db.session.add(hospital)
    db.session.commit()
    
    flash(f'Hospital {nombre} creado correctamente.', 'success')
    return redirect(url_for('admin.hospitales'))

@bp.route('/hospitales/<int:hospital_id>/editar', methods=['POST'])
@admin_required
def hospital_editar(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    
    hospital.nombre = request.form.get('nombre', hospital.nombre).strip()
    hospital.direccion = request.form.get('direccion', hospital.direccion).strip()
    hospital.ciudad = request.form.get('ciudad', hospital.ciudad).strip()
    hospital.telefono = request.form.get('telefono', hospital.telefono).strip()
    hospital.contacto_nombre = request.form.get('contacto_nombre', hospital.contacto_nombre).strip()
    hospital.contacto_email = request.form.get('contacto_email', hospital.contacto_email).strip()
    hospital.contacto_telefono = request.form.get('contacto_telefono', hospital.contacto_telefono).strip()
    hospital.tipo = request.form.get('tipo', hospital.tipo).strip()
    hospital.notas = request.form.get('notas', hospital.notas).strip()
    hospital.activo = request.form.get('activo') == 'on'
    
    db.session.commit()
    flash(f'Hospital {hospital.nombre} actualizado.', 'success')
    return redirect(url_for('admin.hospitales'))

# ============================================================
# GESTION DE MATERIALES (antes servicios)
# ============================================================

@bp.route('/materiales')
@admin_required
def materiales():
    materiales = Material.query.order_by(Material.categoria, Material.nombre).all()
    return render_template('admin/materiales.html', materiales=materiales)

@bp.route('/materiales/nuevo', methods=['POST'])
@admin_required
def material_nuevo():
    nombre = request.form.get('nombre', '').strip()
    categoria = request.form.get('categoria', 'general').strip()
    descripcion = request.form.get('descripcion', '').strip()
    costo_referencia = request.form.get('costo_referencia', 0, type=float)
    
    if not nombre:
        flash('El nombre del material es requerido.', 'warning')
        return redirect(url_for('admin.materiales'))
    
    material = Material(
        nombre=nombre,
        categoria=categoria,
        descripcion=descripcion,
        costo_referencia=costo_referencia
    )
    db.session.add(material)
    db.session.commit()
    
    flash(f'Material {nombre} creado correctamente.', 'success')
    return redirect(url_for('admin.materiales'))

@bp.route('/materiales/<int:material_id>/editar', methods=['POST'])
@admin_required
def material_editar(material_id):
    material = Material.query.get_or_404(material_id)
    
    material.nombre = request.form.get('nombre', material.nombre).strip()
    material.categoria = request.form.get('categoria', material.categoria).strip()
    material.descripcion = request.form.get('descripcion', material.descripcion).strip()
    material.costo_referencia = request.form.get('costo_referencia', float(material.costo_referencia), type=float)
    material.activo = request.form.get('activo') == 'on'
    
    db.session.commit()
    flash(f'Material {material.nombre} actualizado.', 'success')
    return redirect(url_for('admin.materiales'))

# ============================================================
# SISTEMA DE TICKETS (cobros - ahora es el admin quien paga al promotor)
# ============================================================

@bp.route('/tickets')
@admin_required
def tickets():
    estado_filtro = request.args.get('estado', 'todos')
    
    query = Ticket.query
    if estado_filtro != 'todos':
        query = query.filter_by(estado=estado_filtro)
    
    tickets = query.order_by(Ticket.created_at.desc()).all()
    return render_template('admin/tickets.html', tickets=tickets, estado_filtro=estado_filtro)

@bp.route('/tickets/<int:ticket_id>/aprobar', methods=['POST'])
@admin_required
def ticket_aprobar(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket.estado != 'pendiente':
        flash('Este ticket no puede ser aprobado.', 'warning')
        return redirect(url_for('admin.tickets'))
    
    ticket.estado = 'aprobado'
    ticket.fecha_aprobacion = datetime.utcnow()
    ticket.aprobado_por = current_user.id
    db.session.commit()
    
    flash(f'Ticket #{ticket.numero} aprobado correctamente.', 'success')
    return redirect(url_for('admin.tickets'))

@bp.route('/tickets/<int:ticket_id>/pagar', methods=['POST'])
@admin_required
def ticket_pagar(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket.estado not in ['pendiente', 'aprobado']:
        flash('Este ticket no puede ser pagado.', 'warning')
        return redirect(url_for('admin.tickets'))
    
    metodo_pago = request.form.get('metodo_pago', 'transferencia')
    referencia_pago = request.form.get('referencia_pago', '').strip()
    
    ticket.estado = 'pagado'
    ticket.fecha_pago = datetime.utcnow()
    ticket.pagado_por = current_user.id
    ticket.metodo_pago = metodo_pago
    ticket.referencia_pago = referencia_pago
    db.session.commit()
    
    flash(f'Ticket #{ticket.numero} pagado correctamente.', 'success')
    return redirect(url_for('admin.tickets'))

@bp.route('/tickets/<int:ticket_id>/confirmar', methods=['POST'])
@admin_required
def ticket_confirmar(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket.estado not in ['pagado', 'cerrado_por_promotor']:
        flash('Este ticket no puede ser confirmado. Debe estar en estado Pagado o Cerrado por Promotor.', 'warning')
        return redirect(url_for('admin.tickets'))
    
    ticket.estado = 'cobrado'
    ticket.fecha_cobro = datetime.utcnow()
    db.session.commit()
    
    flash(f'Ticket #{ticket.numero} confirmado como cobrado.', 'success')
    return redirect(url_for('admin.tickets'))


@bp.route('/tickets/<int:ticket_id>/rechazar', methods=['POST'])
@admin_required
def ticket_rechazar(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket.estado != 'pendiente':
        flash('Este ticket no puede ser rechazado.', 'warning')
        return redirect(url_for('admin.tickets'))
    
    motivo = request.form.get('motivo_rechazo', '').strip()
    ticket.estado = 'rechazado'
    ticket.descripcion = f"{ticket.descripcion}\nRechazado: {motivo}"
    db.session.commit()
    
    flash(f'Ticket #{ticket.numero} rechazado.', 'info')
    return redirect(url_for('admin.tickets'))

@bp.route('/finanzas')
@admin_required
def finanzas():
    # Obtener parámetros de filtro
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    promotor_id = request.args.get('promotor_id', type=int)
    
    # Construir query base para tickets filtrados
    query = Ticket.query
    
    if fecha_desde:
        try:
            desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            query = query.filter(Ticket.created_at >= desde)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            query = query.filter(Ticket.created_at <= hasta)
        except ValueError:
            pass
    
    if promotor_id:
        query = query.filter_by(usuario_id=promotor_id)
    
    tickets_filtrados = query.order_by(Ticket.created_at.desc()).all()
    
    # ============================================================
    # CÁLCULOS FINANCIEROS REALES (basados en tickets cobrados)
    # ============================================================
    
    # INGRESOS REALES: Tickets en estado 'cobrado' (materiales vendidos)
    tickets_cobrados = Ticket.query.filter_by(estado='cobrado').all()
    total_ingresos = 0
    for t in tickets_cobrados:
        if t.materiales_vendidos:
            for mat in t.materiales_vendidos:
                total_ingresos += float(mat.get('precio_venta', 0)) * int(mat.get('cantidad', 1))
    
    # EGRESOS REALES: Costo de visitas cobradas (lo que paga admin a promotores)
    total_egresos = 0
    for t in tickets_cobrados:
        if t.visita:
            total_egresos += float(t.visita.costo_visita or 0)
    
    # GANANCIA NETA REAL
    ganancia_neta = total_ingresos - total_egresos
    
    # ============================================================
    # PROYECCIONES (tickets aprobados - próximos pagos)
    # ============================================================
    
    tickets_aprobados = Ticket.query.filter_by(estado='aprobado').all()
    total_proyectado_aprobado = sum(float(t.monto) for t in tickets_aprobados)
    
    tickets_pendientes = Ticket.query.filter_by(estado='pendiente').all()
    total_proyectado_pendiente = sum(float(t.monto) for t in tickets_pendientes)
    
    # Proyección total de gastos (lo que se espera pagar)
    proyeccion_gastos = total_proyectado_aprobado + total_proyectado_pendiente
    
    # ============================================================
    # RESUMEN POR ESTADO
    # ============================================================
    resumen_estados = {
        'cobrados': len(tickets_cobrados),
        'aprobados': len(tickets_aprobados),
        'pendientes': len(tickets_pendientes),
        'cerrados_por_promotor': Ticket.query.filter_by(estado='cerrado_por_promotor').count()
    }
    
    # ============================================================
    # TOP PROMOTORES (por ingresos generados - tickets cobrados)
    # ============================================================
    promotores = Usuario.query.filter_by(tipo='promotor').all()
    top_promotores = []
    for p in promotores:
        t_cobrados = Ticket.query.filter_by(usuario_id=p.id, estado='cobrado').all()
        if t_cobrados:
            ingresos_promotor = 0
            for t in t_cobrados:
                if t.materiales_vendidos:
                    for mat in t.materiales_vendidos:
                        ingresos_promotor += float(mat.get('precio_venta', 0)) * int(mat.get('cantidad', 1))
            
            top_promotores.append({
                'promotor': p,
                'total_ingresos': ingresos_promotor,
                'tickets_cobrados': len(t_cobrados),
                'promedio_ticket': ingresos_promotor / len(t_cobrados) if t_cobrados else 0
            })
    
    top_promotores.sort(key=lambda x: x['total_ingresos'], reverse=True)
    top_promotores = top_promotores[:10]
    
    # ============================================================
    # MATERIALES MÁS VENDIDOS (solo tickets cobrados)
    # ============================================================
    from collections import Counter
    material_counter = Counter()
    total_por_material = {}
    
    for t in tickets_cobrados:
        if t.materiales_vendidos:
            for m in t.materiales_vendidos:
                nombre = m.get('nombre', 'Sin nombre')
                cantidad = int(m.get('cantidad', 1))
                precio = float(m.get('precio_venta', 0))
                material_counter[nombre] += cantidad
                total_por_material[nombre] = total_por_material.get(nombre, 0) + (precio * cantidad)
    
    top_materiales = []
    for nombre, cantidad in material_counter.most_common(15):
        top_materiales.append({
            'nombre': nombre,
            'cantidad': cantidad,
            'total_venta': total_por_material.get(nombre, 0)
        })
    
    # ============================================================
    # EVOLUCIÓN MENSUAL (últimos 6 meses)
    # ============================================================
    from calendar import month_name
    hoy = date.today()
    datos_mensuales = []
    
    for i in range(5, -1, -1):
        mes = hoy.month - i
        anio = hoy.year
        while mes <= 0:
            mes += 12
            anio -= 1
        
        # Tickets cobrados este mes (ingresos y egresos reales)
        tickets_mes = Ticket.query.filter(
            db.extract('month', Ticket.fecha_cobro) == mes,
            db.extract('year', Ticket.fecha_cobro) == anio,
            Ticket.estado == 'cobrado'
        ).all()
        
        ingresos_mes = 0
        egresos_mes = 0
        for t in tickets_mes:
            if t.materiales_vendidos:
                for mat in t.materiales_vendidos:
                    ingresos_mes += float(mat.get('precio_venta', 0)) * int(mat.get('cantidad', 1))
            if t.visita:
                egresos_mes += float(t.visita.costo_visita or 0)
        
        # Proyección este mes (aprobados + pendientes)
        tickets_proyectados = Ticket.query.filter(
            db.extract('month', Ticket.created_at) == mes,
            db.extract('year', Ticket.created_at) == anio,
            Ticket.estado.in_(['aprobado', 'pendiente'])
        ).all()
        
        proyeccion_mes = sum(float(t.monto) for t in tickets_proyectados)
        
        datos_mensuales.append({
            'mes': f"{month_name[mes][:3]} {anio}",
            'ingresos': ingresos_mes,
            'egresos': egresos_mes,
            'ganancia': ingresos_mes - egresos_mes,
            'proyeccion': proyeccion_mes
        })
    
    return render_template('admin/finanzas.html',
                         tickets_filtrados=tickets_filtrados,
                         total_ingresos=total_ingresos,
                         total_egresos=total_egresos,
                         ganancia_neta=ganancia_neta,
                         total_proyectado_aprobado=total_proyectado_aprobado,
                         total_proyectado_pendiente=total_proyectado_pendiente,
                         proyeccion_gastos=proyeccion_gastos,
                         resumen_estados=resumen_estados,
                         top_promotores=top_promotores,
                         top_materiales=top_materiales,
                         datos_mensuales=datos_mensuales,
                         promotores=promotores,
                         fecha_desde=fecha_desde,
                         fecha_hasta=fecha_hasta,
                         promotor_id=promotor_id)

# ============================================================
# API PARA ADMIN
# ============================================================

@bp.route('/api/promotor/<int:promotor_id>/resumen')
@admin_required
def api_promotor_resumen(promotor_id):
    promotor = Usuario.query.get_or_404(promotor_id)
    visitas = Visita.query.filter_by(usuario_id=promotor_id).count()
    tickets_pagados = Ticket.query.filter_by(usuario_id=promotor_id, estado='pagado').all()
    tickets_pendientes = Ticket.query.filter_by(usuario_id=promotor_id, estado='pendiente').all()
    
    return jsonify({
        'id': promotor.id,
        'nombre': promotor.nombre,
        'email': promotor.email,
        'region': promotor.region_asignada,
        'total_visitas': visitas,
        'total_cobrado': sum(float(t.monto) for t in tickets_pagados),
        'total_pendiente': sum(float(t.monto) for t in tickets_pendientes),
        'activo': promotor.activo
    })

@bp.route('/api/visita/<int:visita_id>/detalle')
@admin_required
def api_visita_detalle(visita_id):
    visita = Visita.query.get_or_404(visita_id)
    return jsonify({
        'id': visita.id,
        'hospital': visita.hospital.nombre,
        'promotor': visita.promotor.nombre,
        'paciente': visita.paciente_nombre,
        'cirujano': visita.cirujano_nombre,
        'tipo_cirugia': visita.tipo_cirugia,
        'fecha': visita.get_fecha_str(),
        'hora_inicio': visita.get_hora_inicio_str(),
        'hora_fin': visita.get_hora_fin_str(),
        'duracion': visita.duracion_estimada,
        'costo_visita': float(visita.costo_visita),
        'estado': visita.estado,
        'ticket_generado': visita.ticket_generado,
        'materiales': visita.materiales_ofrecidos or []
    })

@bp.route('/tickets/<int:ticket_id>')
@admin_required
def ver_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('admin/ver_ticket.html', ticket=ticket)
