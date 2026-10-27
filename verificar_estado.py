from app import create_app
from app.models import db, Visita, Usuario, Ticket
from datetime import datetime, timedelta, time
import json

app = create_app()
with app.app_context():
    print("=== ESTADO ACTUAL DEL SISTEMA ===\n")
    
    # 1. Ver visitas de oferta
    print("1. VISITAS DE OFERTA:")
    ofertas = Visita.query.filter_by(estado='oferta').all()
    print(f"   Total: {len(ofertas)}")
    for v in ofertas:
        print(f"   - ID {v.id}: {v.paciente_nombre} en {v.hospital.nombre} (promotor: {v.usuario_id})")
    
    # 2. Ver visitas directas
    print("\n2. VISITAS DIRECTAS (programadas):")
    directas = Visita.query.filter_by(estado='programada', modo_asignacion='directo').all()
    print(f"   Total: {len(directas)}")
    for v in directas:
        promotor = Usuario.query.get(v.usuario_id)
        print(f"   - ID {v.id}: {v.paciente_nombre} - Promotor: {promotor.nombre if promotor else 'N/A'}")
    
    # 3. Ver tickets existentes
    print("\n3. TICKETS:")
    tickets = Ticket.query.all()
    print(f"   Total: {len(tickets)}")
    for t in tickets:
        print(f"   - {t.numero}: ${t.monto} - {t.estado}")
    
    # 4. Ver promotores
    print("\n4. PROMOTORES:")
    promotores = [u for u in Usuario.query.all() if not u.es_admin()]
    for p in promotores:
        print(f"   - {p.nombre} (ID: {p.id}, email: {p.email})")
    
    print("\n=== FIN DEL REPORTE ===")
