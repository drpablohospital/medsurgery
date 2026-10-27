from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Visita, Hospital
from datetime import datetime, date

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/visitas')
@login_required
def api_visitas():
    """API para obtener visitas del calendario"""
    fecha_inicio = request.args.get('start')
    fecha_fin = request.args.get('end')
    
    query = Visita.query.filter(Visita.estado.notin_(['cancelada', 'no_show']))
    
    if fecha_inicio:
        query = query.filter(Visita.fecha >= datetime.strptime(fecha_inicio, '%Y-%m-%d').date())
    if fecha_fin:
        query = query.filter(Visita.fecha <= datetime.strptime(fecha_fin, '%Y-%m-%d').date())
    
    # Si no es admin, solo mostrar las propias
    if not current_user.es_admin():
        query = query.filter_by(usuario_id=current_user.id)
    
    visitas = query.order_by(Visita.fecha, Visita.hora_inicio).all()
    
    eventos = []
    for v in visitas:
        eventos.append({
            'id': v.id,
            'title': f"{v.promotor.nombre} - {v.tipo_cirugia or 'Visita'}",
            'start': f"{v.fecha.isoformat()}T{v.hora_inicio.strftime('%H:%M')}",
            'end': f"{v.fecha.isoformat()}T{v.hora_fin.strftime('%H:%M')}",
            'hospital_id': v.hospital_id,
            'estado': v.estado,
            'color': '#2ecc71' if v.estado == 'realizada' else '#3498db' if v.estado == 'programada' else '#e74c3c'
        })
    
    return jsonify(eventos)

@bp.route('/hospitales')
@login_required
def api_hospitales():
    """API para obtener lista de hospitales activos"""
    hospitales = Hospital.query.filter_by(activo=True).all()
    return jsonify([{
        'id': h.id,
        'nombre': h.nombre,
        'ciudad': h.ciudad,
        'direccion': h.direccion,
        'telefono': h.telefono
    } for h in hospitales])
