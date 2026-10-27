from app import create_app
from app.models import db, Visita, Usuario, Ticket, Hospital, Material
from app.utils.helpers import generar_numero_ticket
from datetime import datetime, time
import json

app = create_app()
with app.app_context():
    print("=== SIMULACION DE FLUJO COMPLETO ===\n")
    
    # 1. PROMOTOR TOMA UNA OFERTA
    print("1. PROMOTOR TOMA OFERTA:")
    oferta = Visita.query.filter_by(estado='oferta').first()
    if not oferta:
        print("   ERROR: No hay ofertas disponibles")
        exit()
    
    carlos = Usuario.query.filter_by(email='carlos.mendoza@promocir.com').first()
    if not carlos:
        print("   ERROR: Carlos no encontrado")
        exit()
    
    print(f"   Oferta: ID {oferta.id} - {oferta.paciente_nombre}")
    print(f"   Promotor: {carlos.nombre}")
    
    # Adjudicar la visita
    oferta.usuario_id = carlos.id
    oferta.estado = 'programada'
    db.session.commit()
    print(f"   RESULTADO: Visita adjudicada a {carlos.nombre}")
    
    # 2. COMPLETAR VISITA CON VENTA REAL
    print("\n2. COMPLETAR VISITA CON VENTA REAL:")
    visita = Visita.query.get(oferta.id)
    
    # Registrar venta real
    visita.detalle = {
        'venta': {
            'venta_realizada': True,
            'material_id': 1,
            'material_nombre': 'Malla Prolene',
            'cantidad': 2,
            'monto': 8500.00,
            'notas': 'El hospital compro 2 mallas para el procedimiento'
        }
    }
    visita.estado = 'realizada'
    db.session.commit()
    print(f"   RESULTADO: Venta registrada - $8,500.00")
    print(f"   Material: Malla Prolene (x2)")
    
    # 3. GENERAR TICKET DE COBRO
    print("\n3. GENERAR TICKET DE COBRO:")
    numero = generar_numero_ticket()
    ticket = Ticket(
        usuario_id=carlos.id,
        visita_id=visita.id,
        numero=numero,
        monto=visita.costo_visita,
        estado='pendiente',
        descripcion=f"Cobro por visita programada - {visita.paciente_nombre}",
        detalle={
            'hospital': visita.hospital.nombre,
            'promotor': carlos.nombre,
            'fecha': visita.get_fecha_str(),
            'hora': visita.get_hora_inicio_str(),
            'paciente': visita.paciente_nombre,
            'cirujano': visita.cirujano_nombre,
            'tipo_cirugia': visita.tipo_cirugia,
            'monto': float(visita.costo_visita)
        }
    )
    db.session.add(ticket)
    db.session.commit()
    print(f"   RESULTADO: Ticket {numero} generado - ${visita.costo_visita}")
    
    # 4. VERIFICAR FINANZAS
    print("\n4. ESTADO DE FINANZAS:")
    total_ventas = 0
    for v in Visita.query.filter_by(estado='realizada').all():
        if v.detalle and 'venta' in v.detalle:
            venta_data = v.detalle['venta']
            if venta_data.get('venta_realizada'):
                total_ventas += float(venta_data.get('monto', 0))
    
    print(f"   Total Ventas Reales: ${total_ventas:.2f}")
    print(f"   Total Tickets: {Ticket.query.count()}")
    print(f"   Tickets Pendientes: {Ticket.query.filter_by(estado='pendiente').count()}")
    print(f"   Tickets Pagados: {Ticket.query.filter_by(estado='pagado').count()}")
    
    print("\n=== FLUJO COMPLETADO CON EXITO ===")
