from datetime import datetime, time
import uuid

def format_currency(value):
    """Formatea un valor como moneda mexicana"""
    if value is None:
        return "$0.00"
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def format_datetime(value, format='%d/%m/%Y %H:%M'):
    """Formatea una fecha/datetime"""
    if value is None:
        return ''
    if isinstance(value, datetime):
        return value.strftime(format)
    return str(value)

def generar_numero_ticket():
    """Genera un número de ticket único"""
    from app.models import Ticket
    from app import db
    
    # Formato: TKT-YYYYMMDD-XXXX
    prefix = datetime.now().strftime('TKT-%Y%m%d-')
    
    # Buscar último número del día
    last_ticket = Ticket.query.filter(
        Ticket.numero.like(f'{prefix}%')
    ).order_by(Ticket.id.desc()).first()
    
    if last_ticket:
        parts = last_ticket.numero.split('-')
        try:
            last_num = int(parts[-1])
            new_num = last_num + 1
        except ValueError:
            new_num = 1
    else:
        new_num = 1
    
    return f"{prefix}{new_num:04d}"

def calcular_duracion(hora_inicio, hora_fin):
    """Calcula duración en minutos entre dos objetos time"""
    if isinstance(hora_inicio, str):
        h, m = map(int, hora_inicio.split(':'))
        hora_inicio = time(h, m)
    if isinstance(hora_fin, str):
        h, m = map(int, hora_fin.split(':'))
        hora_fin = time(h, m)
    
    inicio_min = hora_inicio.hour * 60 + hora_inicio.minute
    fin_min = hora_fin.hour * 60 + hora_fin.minute
    
    if fin_min < inicio_min:
        fin_min += 24 * 60
    
    return fin_min - inicio_min

def verificar_disponibilidad(hospital_id, fecha, hora_inicio, hora_fin, visita_id=None):
    """
    Verifica disponibilidad de un hospital en un horario específico.
    Retorna (disponible, conflictos)
    """
    from app.models import Visita
    
    query = Visita.query.filter(
        Visita.hospital_id == hospital_id,
        Visita.fecha == fecha,
        Visita.estado.notin_(['cancelada', 'no_show'])
    )
    
    if visita_id:
        query = query.filter(Visita.id != visita_id)
    
    conflictos = 0
    for visita in query.all():
        # Verificar solapamiento de horarios
        vi = visita.hora_inicio.hour * 60 + visita.hora_inicio.minute
        vf = visita.hora_fin.hour * 60 + visita.hora_fin.minute
        ni = hora_inicio.hour * 60 + hora_inicio.minute
        nf = hora_fin.hour * 60 + hora_fin.minute
        
        # Hay solapamiento si no son completamente disjuntos
        if not (nf <= vi or ni >= vf):
            conflictos += 1
    
    return conflictos == 0, conflictos
