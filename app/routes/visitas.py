from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import db, Visita, Hospital, Material, Ticket, Usuario
from app.utils.decorators import promotor_required, admin_required
from app.utils.helpers import verificar_disponibilidad, generar_numero_ticket, calcular_duracion
from datetime import datetime as dt, date, time, timedelta
import json

bp = Blueprint('visitas', __name__, url_prefix='/visitas')

@bp.route('/')
@login_required
def calendario():
    hospitales = Hospital.query.filter_by(activo=True).all()
    
    fecha_str = request.args.get('fecha', date.today().isoformat())
    try:
        fecha_actual = dt.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha_actual = date.today()
    
    return render_template('calendario.html',
                         hospitales=hospitales,
                         fecha_actual=fecha_actual)

@bp.route('/api/disponibilidad')
@login_required
def api_disponibilidad():
    hospital_id = request.args.get('hospital_id')
    fecha_str = request.args.get('fecha')
    
    if not fecha_str:
        return jsonify({'error': 'Faltan parametros'}), 400
    
    try:
        fecha = dt.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Fecha invalida'}), 400
    
    # Obtener visitas del mes completo
    from calendar import monthrange
    year = fecha.year
    month = fecha.month
    _, last_day = monthrange(year, month)
    
    # Construir query base
    query = Visita.query.filter(
        Visita.fecha >= date(year, month, 1),
        Visita.fecha <= date(year, month, last_day),
        Visita.estado.notin_(['cancelada', 'no_show'])
    )
    
    # Filtrar por hospital si se especifica
    if hospital_id and hospital_id.strip():
        query = query.filter(Visita.hospital_id == int(hospital_id))
    
    visitas = query.order_by(Visita.hora_inicio).all()
    
    eventos = []
    for v in visitas:
        # Manejar visitas sin promotor (ofertas no adjudicadas)
        promotor_nombre = v.promotor.nombre if v.promotor else 'Sin asignar'
        eventos.append({
            'id': v.id,
            'title': f"{promotor_nombre} - {v.tipo_cirugia or 'Visita'}",
            'start': f"{v.fecha.isoformat()}T{v.hora_inicio.strftime('%H:%M')}",
            'end': f"{v.fecha.isoformat()}T{v.hora_fin.strftime('%H:%M')}",
            'hospital_id': v.hospital_id,
            'estado': v.estado,
            'promotor': promotor_nombre,
            'es_mia': v.usuario_id == current_user.id
        })
    
    return jsonify(eventos)

@bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    hospitales = Hospital.query.filter_by(activo=True).all()
    materiales = Material.query.filter_by(activo=True).all()
    
    if request.method == 'POST':
        hospital_id = request.form.get('hospital_id', type=int)
        paciente_nombre = request.form.get('paciente_nombre', '').strip()
        paciente_edad = request.form.get('paciente_edad', type=int)
        cirujano_nombre = request.form.get('cirujano_nombre', '').strip()
        cirujano_especialidad = request.form.get('cirujano_especialidad', '').strip()
        tipo_cirugia = request.form.get('tipo_cirugia', '').strip()
        fecha_str = request.form.get('fecha')
        hora_inicio_str = request.form.get('hora_inicio')
        duracion = request.form.get('duracion_estimada', type=int)
        costo_visita = request.form.get('costo_visita', type=float)
        especificaciones = request.form.get('especificaciones', '').strip()
        
        if not all([hospital_id, paciente_nombre, cirujano_nombre, tipo_cirugia, fecha_str, hora_inicio_str, duracion]):
            flash('Todos los campos obligatorios son requeridos.', 'warning')
            return render_template('nueva_visita.html', hospitales=hospitales, materiales=materiales)
        
        try:
            fecha = dt.strptime(fecha_str, '%Y-%m-%d').date()
            hora_inicio = dt.strptime(hora_inicio_str, '%H:%M').time()
        except ValueError:
            flash('Fecha u hora invalida.', 'warning')
            return render_template('nueva_visita.html', hospitales=hospitales, materiales=materiales)
        
        inicio_dt = dt.combine(fecha, hora_inicio)
        fin_dt = inicio_dt + timedelta(minutes=duracion)
        hora_fin = fin_dt.time()
        
        if fecha < date.today() or (fecha == date.today() and hora_inicio < dt.now().time()):
            flash('No puedes agendar visitas en el pasado.', 'warning')
            return render_template('nueva_visita.html', hospitales=hospitales, materiales=materiales)
        
        disponible, conflictos = verificar_disponibilidad(
            hospital_id, fecha, hora_inicio, hora_fin
        )
        
        if not disponible:
            flash(f'El hospital no esta disponible en ese horario. ({conflictos} conflicto(s))', 'danger')
            return render_template('nueva_visita.html', hospitales=hospitales, materiales=materiales)
        
        # Materiales seleccionados
        materiales_seleccionados = []
        materiales_ids = request.form.getlist('materiales[]')
        for mid in materiales_ids:
            material = Material.query.get(int(mid))
            if material:
                materiales_seleccionados.append({
                    'id': material.id,
                    'nombre': material.nombre,
                    'categoria': material.categoria
                })
        
        # Si es admin, puede elegir modo de asignacion
        modo_asignacion = 'directo'
        usuario_asignado_id = current_user.id
        
        if current_user.es_admin():
            modo_asignacion = request.form.get('modo_asignacion', 'directo')
            if modo_asignacion == 'directo':
                promotor_id = request.form.get('promotor_id', type=int)
                if promotor_id:
                    usuario_asignado_id = promotor_id
                else:
                    flash('Debes seleccionar un promotor para asignacion directa.', 'warning')
                    promotores = Usuario.query.filter_by(tipo='promotor', activo=True).all()
                    return render_template('nueva_visita.html', hospitales=hospitales, materiales=materiales, promotores=promotores)
            # Si es 'oferta', el usuario_id sera 0 temporalmente hasta que un promotor se adjudique
            elif modo_asignacion == 'oferta':
                usuario_asignado_id = None  # Temporal: NULL indica visita sin asignar
        
        visita = Visita(
            usuario_id=usuario_asignado_id,
            hospital_id=hospital_id,
            paciente_nombre=paciente_nombre,
            paciente_edad=paciente_edad,
            cirujano_nombre=cirujano_nombre,
            cirujano_especialidad=cirujano_especialidad,
            tipo_cirugia=tipo_cirugia,
            materiales_ofrecidos=materiales_seleccionados,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_estimada=duracion,
            costo_visita=costo_visita or 0.00,
            especificaciones=especificaciones,
            modo_asignacion=modo_asignacion
        )
        
        db.session.add(visita)
        db.session.commit()
        
        # Generar ticket automáticamente para la visita
        from app.models import Ticket
        
        # Generar número de ticket
        
        fecha_str = dt.now().strftime('%Y%m%d')
        ticket_num = f'T-{fecha_str}-{visita.id:04d}'
        
        ticket = Ticket(
            visita_id=visita.id,
            usuario_id=usuario_asignado_id,  # Puede ser None si es oferta
            numero=ticket_num,
            estado='oferta' if modo_asignacion == 'oferta' else 'pendiente',
            monto=costo_visita or 0.00,
            materiales_vendidos=materiales_seleccionados,
            detalle=especificaciones or 'Ticket generado automáticamente desde visita',
            descripcion=f'Visita programada en {visita.hospital.nombre}'
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        if modo_asignacion == 'oferta':
            flash(f'Visita publicada en oferta. Los promotores pueden adjudicarsela.', 'success')
        else:
            flash(f'Visita programada correctamente en {visita.hospital.nombre}. Ticket #{ticket.id} generado.', 'success')
        return redirect(url_for('visitas.calendario'))
    
    # Si es admin, pasar lista de promotores
    promotores = None
    if current_user.es_admin():
        promotores = Usuario.query.filter_by(tipo='promotor', activo=True).all()
    
    return render_template('nueva_visita.html', hospitales=hospitales, materiales=materiales, promotores=promotores)

@bp.route('/<int:visita_id>')
@login_required
def detalle(visita_id):
    visita = Visita.query.get_or_404(visita_id)
    
    if visita.usuario_id != current_user.id and not current_user.es_admin():
        flash('No tienes permiso para ver esta visita.', 'danger')
        return redirect(url_for('visitas.calendario'))
    
    return render_template('detalle_visita.html', visita=visita)

@bp.route('/<int:visita_id>/cancelar', methods=['POST'])
@login_required
def cancelar(visita_id):
    visita = Visita.query.get_or_404(visita_id)
    
    if visita.usuario_id != current_user.id and not current_user.es_admin():
        flash('No tienes permiso para cancelar esta visita.', 'danger')
        return redirect(url_for('visitas.calendario'))
    
    visita.estado = 'cancelada'
    db.session.commit()
    
    flash('Visita cancelada correctamente.', 'info')
    return redirect(url_for('visitas.calendario'))

@bp.route('/<int:visita_id>/realizar', methods=['POST'])
@login_required
def marcar_realizada(visita_id):
    visita = Visita.query.get_or_404(visita_id)
    
    if visita.usuario_id != current_user.id and not current_user.es_admin():
        flash('No tienes permiso para modificar esta visita.', 'danger')
        return redirect(url_for('visitas.calendario'))
    
    visita.estado = 'realizada'
    db.session.commit()
    
    flash('Visita marcada como realizada. Ahora puedes generar el ticket de cobro.', 'success')
    return redirect(url_for('visitas.detalle', visita_id=visita.id))

@bp.route('/<int:visita_id>/ticket', methods=['POST'])
@bp.route('/<int:visita_id>/ticket', methods=['GET', 'POST'])
@login_required
def generar_ticket(visita_id):
    visita = Visita.query.get_or_404(visita_id)
    
    if visita.usuario_id != current_user.id:
        flash('No tienes permiso para generar ticket de esta visita.', 'danger')
        return redirect(url_for('visitas.calendario'))
    
    if visita.estado != 'realizada':
        flash('Solo se pueden generar tickets de visitas realizadas.', 'warning')
        return redirect(url_for('visitas.detalle', visita_id=visita.id))
    
    if visita.ticket_generado:
        flash('Esta visita ya tiene un ticket generado.', 'info')
        return redirect(url_for('visitas.detalle', visita_id=visita.id))
    
    # Obtener materiales ofrecidos en esta visita
    materiales_ofrecidos = visita.materiales_ofrecidos or []
    
    if request.method == 'POST':
        # Procesar materiales vendidos
        materiales_vendidos = []
        total_venta = 0
        
        for i, mat in enumerate(materiales_ofrecidos):
            vendido = request.form.get(f'material_vendido_{i}') == 'on'
            if vendido:
                cantidad = request.form.get(f'cantidad_{i}', type=int) or 1
                precio_venta = request.form.get(f'precio_venta_{i}', type=float) or 0
                
                materiales_vendidos.append({
                    'id': mat.get('id'),
                    'nombre': mat.get('nombre'),
                    'categoria': mat.get('categoria'),
                    'cantidad': cantidad,
                    'precio_venta': precio_venta
                })
                total_venta += precio_venta * cantidad
        
        # Monto de honorarios del promotor
        monto = float(visita.costo_visita)
        
        # Crear ticket
        ticket_num = generar_numero_ticket()
        
        ticket = Ticket(
            usuario_id=current_user.id,
            visita_id=visita.id,
            numero=ticket_num,
            monto=monto,
            descripcion=f'Ticket de cobro por visita a {visita.hospital.nombre}',
            detalle={
                'visita_id': visita.id,
                'hospital': visita.hospital.nombre,
                'promotor': visita.promotor.nombre,
                'fecha': visita.get_fecha_str(),
                'hora': visita.get_hora_inicio_str(),
                'paciente': visita.paciente_nombre,
                'cirujano': visita.cirujano_nombre,
                'tipo_cirugia': visita.tipo_cirugia,
                'materiales_ofrecidos': materiales_ofrecidos,
                'monto': monto,
                'total_venta_materiales': total_venta
            },
            materiales_vendidos=materiales_vendidos
        )
        db.session.add(ticket)
        db.session.commit()
        
        # Actualizar visita
        visita.ticket_generado = True
        visita.ticket_id = ticket.id
        db.session.commit()
        
        flash(f'Ticket #{ticket_num} generado correctamente. Total venta materiales: ', 'success')
        return redirect(url_for('visitas.detalle', visita_id=visita.id))
    
    # GET: mostrar formulario
    return render_template('generar_ticket.html', visita=visita, materiales=materiales_ofrecidos)

# OFERTAS - Sistema de visitas en oferta para promotores
# ============================================================================

@bp.route('/ofertas')
@promotor_required
def ofertas():
    """Vista de visitas en oferta disponibles para promotores"""
    # Visitas en modo 'oferta' que aun no tienen promotor asignado (usuario_id=None)
    # y que estan programadas para hoy o futuro
    visitas_oferta = Visita.query.filter(
        Visita.modo_asignacion == 'oferta',
        Visita.usuario_id.is_(None),
        Visita.estado == 'programada',
        Visita.fecha >= date.today()
    ).order_by(Visita.fecha, Visita.hora_inicio).all()
    
    return render_template('visitas/ofertas.html', visitas=visitas_oferta)

@bp.route('/<int:visita_id>/adjudicar', methods=['POST'])
@promotor_required
def adjudicar_visita(visita_id):
    """Permite a un promotor adjudicarse una visita en oferta"""
    visita = Visita.query.get_or_404(visita_id)
    
    # Verificar que la visita este en modo oferta y sin asignar
    if visita.modo_asignacion != 'oferta' or visita.usuario_id is not None:
        flash('Esta visita ya no esta disponible.', 'danger')
        return redirect(url_for('visitas.ofertas'))
    
    # Verificar que no haya conflictos de horario con otras visitas del promotor
    conflictos = Visita.query.filter(
        Visita.usuario_id == current_user.id,
        Visita.fecha == visita.fecha,
        Visita.estado.notin_(['cancelada', 'no_show']),
        Visita.id != visita.id
    ).filter(
        db.or_(
            db.and_(Visita.hora_inicio <= visita.hora_inicio, Visita.hora_fin > visita.hora_inicio),
            db.and_(Visita.hora_inicio < visita.hora_fin, Visita.hora_fin >= visita.hora_fin)
        )
    ).count()
    
    if conflictos > 0:
        flash('Tienes una visita programada en ese horario. No puedes adjudicarte esta oferta.', 'warning')
        return redirect(url_for('visitas.ofertas'))
    
    # Asignar la visita al promotor actual
    visita.usuario_id = current_user.id
    visita.modo_asignacion = 'directo'  # Una vez adjudicada, pasa a modo directo
    
    # Generar ticket automaticamente para el promotor
    from app.utils.helpers import generar_numero_ticket
    ticket_num = generar_numero_ticket()
    
    ticket = Ticket(
        usuario_id=current_user.id,
        visita_id=visita.id,
        numero=ticket_num,
        monto=float(visita.costo_visita),
        descripcion=f'Ticket de cobro por visita a {visita.hospital.nombre}',
        detalle={
            'visita_id': visita.id,
            'hospital': visita.hospital.nombre,
            'promotor': current_user.nombre,
            'fecha': visita.get_fecha_str(),
            'hora': visita.get_hora_inicio_str(),
            'paciente': visita.paciente_nombre,
            'cirujano': visita.cirujano_nombre,
            'tipo_cirugia': visita.tipo_cirugia,
            'monto': float(visita.costo_visita),
            'total_venta_materiales': 0
        },
        materiales_vendidos=[]
    )
    db.session.add(ticket)
    db.session.commit()
    
    # Actualizar visita con referencia al ticket
    visita.ticket_generado = True
    visita.ticket_id = ticket.id
    db.session.commit()
    
    flash(f'Visita adjudicada correctamente en {visita.hospital.nombre}. Ticket #{ticket_num} generado.', 'success')
    return redirect(url_for('visitas.calendario'))

# ============================================================================
# VENTA REAL - Registro de venta al completar visita
# ============================================================================

@bp.route('/<int:visita_id>/venta', methods=['GET', 'POST'])
@login_required
def registrar_venta(visita_id):
    """Registra la venta real realizada durante una visita"""
    visita = Visita.query.get_or_404(visita_id)
    
    # Solo promotores asignados o admins pueden registrar venta
    if visita.usuario_id != current_user.id and not current_user.es_admin():
        flash('No tienes permiso para registrar venta de esta visita.', 'danger')
        return redirect(url_for('visitas.calendario'))
    
    if visita.estado != 'realizada':
        flash('Solo se pueden registrar ventas de visitas realizadas.', 'warning')
        return redirect(url_for('visitas.detalle', visita_id=visita.id))
    
    # Obtener materiales disponibles
    materiales = Material.query.filter_by(activo=True).all()
    
    if request.method == 'POST':
        venta_realizada = request.form.get('venta_realizada') == 'si'
        
        if venta_realizada:
            material_id = request.form.get('material_vendido', type=int)
            cantidad = request.form.get('cantidad_vendida', type=int)
            monto_venta = request.form.get('monto_venta', type=float)
            notas_venta = request.form.get('notas_venta', '').strip()
            
            if not all([material_id, cantidad, monto_venta]):
                flash('Debes completar todos los campos de la venta.', 'warning')
                return render_template('visitas/registrar_venta.html', visita=visita, materiales=materiales)
            
            material = Material.query.get(material_id)
            if not material:
                flash('Material no encontrado.', 'danger')
                return render_template('visitas/registrar_venta.html', visita=visita, materiales=materiales)
            
            # Guardar datos de venta en la visita
            if not visita.detalle:
                visita.detalle = {}
            
            visita.detalle['venta'] = {
                'material_id': material_id,
                'material_nombre': material.nombre,
                'cantidad': cantidad,
                'monto': monto_venta,
                'notas': notas_venta,
                'registrado_por': current_user.nombre,
                'fecha_registro': dt.now().isoformat()
            }
            
            db.session.commit()
            flash(f'Venta registrada: {cantidad}x {material.nombre} = ${monto_venta:,.2f} MXN', 'success')
        else:
            # No se realizo venta
            if not visita.detalle:
                visita.detalle = {}
            visita.detalle['venta'] = {'venta_realizada': False}
            db.session.commit()
            flash('Registrado: No se realizo venta en esta visita.', 'info')
        
        return redirect(url_for('visitas.detalle', visita_id=visita.id))
    
    return render_template('visitas/registrar_venta.html', visita=visita, materiales=materiales)

# ============================================================================
# HISTORIAL DE TICKETS DEL PROMOTOR (Rentabilidad)
# ============================================================================

@bp.route('/mis-tickets')
@login_required
def mis_tickets():
    """Vista de historial de tickets del promotor con métricas de rentabilidad"""
    if current_user.es_admin():
        return redirect(url_for('admin.tickets'))
    
    # Todos los tickets del promotor
    tickets = Ticket.query.filter_by(usuario_id=current_user.id)        .order_by(Ticket.created_at.desc()).all()
    
    # Métricas
    total_cobrado = sum(float(t.monto) for t in tickets if t.estado == 'pagado')
    total_pendiente = sum(float(t.monto) for t in tickets if t.estado == 'pendiente')
    total_aprobado = sum(float(t.monto) for t in tickets if t.estado == 'aprobado')
    
    # Venta de materiales (ingresos para la organización)
    total_venta_materiales = 0
    for t in tickets:
        if t.materiales_vendidos:
            for mat in t.materiales_vendidos:
                total_venta_materiales += float(mat.get('precio_venta', 0)) * mat.get('cantidad', 1)
    
    # Rentabilidad del promotor = venta de materiales / honorarios pagados
    rentabilidad = (total_venta_materiales / total_cobrado * 100) if total_cobrado > 0 else 0
    
    return render_template('visitas/mis_tickets.html',
                         tickets=tickets,
                         total_cobrado=total_cobrado,
                         total_pendiente=total_pendiente,
                         total_aprobado=total_aprobado,
                         total_venta_materiales=total_venta_materiales,
                         rentabilidad=rentabilidad)

@bp.route('/mis-tickets/<int:ticket_id>/cerrar', methods=['GET', 'POST'])
@promotor_required
def cerrar_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Verificar que el ticket pertenezca al promotor actual
    if ticket.usuario_id != current_user.id:
        flash('No tienes permiso para cerrar este ticket.', 'danger')
        return redirect(url_for('visitas.mis_tickets'))
    
    # Verificar que el ticket esté en estado pendiente
    if ticket.estado != 'pendiente':
        flash('Solo puedes cerrar tickets pendientes.', 'warning')
        return redirect(url_for('visitas.mis_tickets'))
    
    if request.method == 'POST':
        # Procesar cierre de ticket
        monto_declarado = request.form.get('monto_declarado', type=float)
        materiales_vendidos_json = request.form.get('materiales_vendidos', '[]')
        notas_cierre = request.form.get('notas_cierre', '').strip()
        
        # Validar monto
        if not monto_declarado or monto_declarado <= 0:
            flash('El monto declarado es requerido y debe ser mayor a 0.', 'danger')
            return redirect(url_for('visitas.cerrar_ticket', ticket_id=ticket_id))
        
        # Procesar factura adjunta
        factura_url = None
        if 'factura' in request.files:
            factura = request.files['factura']
            if factura and factura.filename:
                # Guardar factura
                import os
                from werkzeug.utils import secure_filename
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'facturas')
                os.makedirs(upload_dir, exist_ok=True)
                filename = secure_filename(f"{ticket.numero}_{factura.filename}")
                factura_path = os.path.join(upload_dir, filename)
                factura.save(factura_path)
                factura_url = f"uploads/facturas/{filename}"
        
        # Actualizar ticket
        ticket.monto = monto_declarado
        try:
            ticket.materiales_vendidos = json.loads(materiales_vendidos_json) if materiales_vendidos_json else []
        except json.JSONDecodeError:
            ticket.materiales_vendidos = []
        ticket.notas_cierre = notas_cierre
        ticket.factura_url = factura_url
        ticket.fecha_cierre_promotor = dt.utcnow()
        ticket.estado = 'cerrado_por_promotor'
        
        db.session.commit()
        
        flash('Ticket cerrado exitosamente. Esperando revisión del administrador.', 'success')
        return redirect(url_for('visitas.mis_tickets'))
    
    # GET: Mostrar formulario de cierre
    return render_template('visitas/cerrar_ticket.html', ticket=ticket, materiales_admin=Material.query.filter_by(activo=True).all())
