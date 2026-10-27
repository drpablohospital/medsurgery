"""
Script de prueba para PromoCir.
Crea 2 usuarios de prueba, visitas de ejemplo y tickets para testear el flujo completo.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.models import db, Usuario, Hospital, Material, Visita, Ticket
from datetime import datetime, date, time, timedelta
from sqlalchemy import inspect

def crear_datos_prueba():
    app = create_app('development')
    
    with app.app_context():
        print("🧪 Creando datos de prueba...")
        
        # ============================================================
        # 1. CREAR USUARIOS DE PRUEBA
        # ============================================================
        
        # Promotor 1: Carlos Mendoza
        promotor1 = Usuario.query.filter_by(email='carlos.mendoza@promocir.com').first()
        if not promotor1:
            promotor1 = Usuario(
                nombre='Carlos Mendoza',
                email='carlos.mendoza@promocir.com',
                tipo='promotor',
                telefono='4421123456',
                region_asignada='Centro-Norte',
                activo=True
            )
            promotor1.set_password('promotor123')
            db.session.add(promotor1)
            print("✅ Promotor 1 creado: carlos.mendoza@promocir.com / promotor123")
        else:
            print("✅ Promotor 1 ya existe")
        
        # Promotor 2: Ana López
        promotor2 = Usuario.query.filter_by(email='ana.lopez@promocir.com').first()
        if not promotor2:
            promotor2 = Usuario(
                nombre='Ana López',
                email='ana.lopez@promocir.com',
                tipo='promotor',
                telefono='4422234567',
                region_asignada='Sur-Oeste',
                activo=True
            )
            promotor2.set_password('promotor123')
            db.session.add(promotor2)
            print("✅ Promotor 2 creado: ana.lopez@promocir.com / promotor123")
        else:
            print("✅ Promotor 2 ya existe")
        
        db.session.commit()
        
        # ============================================================
        # 2. CREAR VISITAS DE PRUEBA
        # ============================================================
        
        hoy = date.today()
        manana = hoy + timedelta(days=1)
        pasado = hoy + timedelta(days=2)
        ayer = hoy - timedelta(days=1)
        
        # Obtener hospitales
        hospital1 = Hospital.query.filter_by(nombre='Hospital Ángeles Querétaro').first()
        hospital2 = Hospital.query.filter_by(nombre='Hospital Star Médica Querétaro').first()
        hospital3 = Hospital.query.filter_by(nombre='Hospital San José del Carmen').first()
        hospital4 = Hospital.query.filter_by(nombre='Hospital General de Querétaro').first()
        
        # Visita 1: Programada para mañana
        if not Visita.query.filter_by(paciente_nombre='María García').first():
            visita1 = Visita(
                usuario_id=promotor1.id,
                hospital_id=hospital1.id if hospital1 else 1,
                paciente_nombre='María García',
                paciente_edad=45,
                cirujano_nombre='Dr. Roberto Sánchez',
                cirujano_especialidad='Cirujano General',
                tipo_cirugia='Colecistectomía Laparoscópica',
                materiales_ofrecidos=[
                    {'id': 1, 'nombre': 'Stapler Circular Endoscópico', 'categoria': 'Laparoscopia'},
                    {'id': 2, 'nombre': 'Trocar 12mm', 'categoria': 'Laparoscopia'}
                ],
                fecha=manana,
                hora_inicio=time(9, 0),
                hora_fin=time(10, 30),
                duracion_estimada=90,
                costo_visita=2500.00,
                estado='programada',
                especificaciones='Requiere video de alta definición para demostración del equipo.',
                notas_seguimiento='Contactar al coordinador de compras previo a la visita.'
            )
            db.session.add(visita1)
            print("✅ Visita 1 creada: María García en Hospital Ángeles")
        
        # Visita 2: Confirmada para pasado mañana
        if not Visita.query.filter_by(paciente_nombre='Pedro Hernández').first():
            visita2 = Visita(
                usuario_id=promotor1.id,
                hospital_id=hospital2.id if hospital2 else 2,
                paciente_nombre='Pedro Hernández',
                paciente_edad=62,
                cirujano_nombre='Dra. Patricia Vega',
                cirujano_especialidad='Gastroenteróloga',
                tipo_cirugia='Hernioplastía Inguinal con Malla',
                materiales_ofrecidos=[
                    {'id': 6, 'nombre': 'Malla Prolén 15x20cm', 'categoria': 'Cirugía General'},
                    {'id': 7, 'nombre': 'Malla Ultrapro 10x15cm', 'categoria': 'Cirugía General'}
                ],
                fecha=pasado,
                hora_inicio=time(14, 0),
                hora_fin=time(15, 30),
                duracion_estimada=90,
                costo_visita=1800.00,
                estado='confirmada',
                especificaciones='Demostración completa de sistema de malla reabsorbible.',
                notas_seguimiento='La Dra. Vega muestra interés en cambio de proveedor actual.'
            )
            db.session.add(visita2)
            print("✅ Visita 2 creada: Pedro Hernández en Star Médica")
        
        # Visita 3: Realizada (ayer) - Promotor 2
        if not Visita.query.filter_by(paciente_nombre='Luis Ramírez').first():
            visita3 = Visita(
                usuario_id=promotor2.id,
                hospital_id=hospital3.id if hospital3 else 3,
                paciente_nombre='Luis Ramírez',
                paciente_edad=38,
                cirujano_nombre='Dr. Miguel Ángel Torres',
                cirujano_especialidad='Ortopedista',
                tipo_cirugia='Artroscopía de Rodilla',
                materiales_ofrecidos=[
                    {'id': 13, 'nombre': 'Prótesis Rodilla Total', 'categoria': 'Ortopedia'}
                ],
                fecha=ayer,
                hora_inicio=time(10, 0),
                hora_fin=time(11, 0),
                duracion_estimada=60,
                costo_visita=1500.00,
                estado='realizada',
                especificaciones='El Dr. Torres quedó muy satisfecho con la demostración. Solicita cotización formal.',
                notas_seguimiento='Enviar cotización antes del viernes. Posible cierre en 2 semanas.'
            )
            db.session.add(visita3)
            print("✅ Visita 3 creada: Luis Ramírez (REALIZADA) en San José del Carmen")
        
        # Visita 4: Realizada (ayer) - Promotor 1
        if not Visita.query.filter_by(paciente_nombre='Carmen Flores').first():
            visita4 = Visita(
                usuario_id=promotor1.id,
                hospital_id=hospital4.id if hospital4 else 4,
                paciente_nombre='Carmen Flores',
                paciente_edad=55,
                cirujano_nombre='Dra. Laura Jiménez',
                cirujano_especialidad='Cirujana Cardiovascular',
                tipo_cirugia='Revascularización Coronaria',
                materiales_ofrecidos=[
                    {'id': 18, 'nombre': 'Stent Coronario Drug-Eluting', 'categoria': 'Cardiología'},
                    {'id': 19, 'nombre': 'Balón Angioplastía', 'categoria': 'Cardiología'}
                ],
                fecha=ayer,
                hora_inicio=time(16, 0),
                hora_fin=time(17, 0),
                duracion_estimada=60,
                costo_visita=3200.00,
                estado='realizada',
                especificaciones='La Dra. Jiménez requiere validación con comité de compras del hospital.',
                notas_seguimiento='Seguimiento en 1 semana con coordinador de compras.'
            )
            db.session.add(visita4)
            print("✅ Visita 4 creada: Carmen Flores (REALIZADA) en Hospital General")
        
        # Visita 5: Programada para hoy
        if not Visita.query.filter_by(paciente_nombre='Jorge Martínez').first():
            visita5 = Visita(
                usuario_id=promotor2.id,
                hospital_id=hospital1.id if hospital1 else 1,
                paciente_nombre='Jorge Martínez',
                paciente_edad=41,
                cirujano_nombre='Dr. Fernando Castro',
                cirujano_especialidad='Neurocirujano',
                tipo_cirugia='Craneotomía Descompresiva',
                materiales_ofrecidos=[
                    {'id': 16, 'nombre': 'Drenaje Ventricular', 'categoria': 'Neurocirugía'}
                ],
                fecha=hoy,
                hora_inicio=time(11, 0),
                hora_fin=time(12, 0),
                duracion_estimada=60,
                costo_visita=2000.00,
                estado='programada',
                especificaciones='Urgente - Paciente grave. Demostrar sistema de monitoreo intracraneal.',
                notas_seguimiento='Confirmar disponibilidad de Dr. Castro 1 hora antes.'
            )
            db.session.add(visita5)
            print("✅ Visita 5 creada: Jorge Martínez (HOY) en Hospital Ángeles")
        
        db.session.commit()
        
        # ============================================================
        # 3. CREAR TICKETS DE PRUEBA (basados en visitas realizadas)
        # ============================================================
        
        # Ticket 1: Pendiente para visita 3
        if not Ticket.query.filter_by(usuario_id=promotor2.id).first():
            ticket1 = Ticket(
                usuario_id=promotor2.id,
                visita_id=visita3.id,
                numero='TKT-20261021-001',
                monto=1500.00,
                estado='pendiente',
                descripcion='Ticket de cobro por visita a Hospital San José del Carmen - Artroscopía de Rodilla',
                detalle={
                    'visita_id': visita3.id,
                    'hospital': 'Hospital San José del Carmen',
                    'promotor': 'Ana López',
                    'fecha': ayer.strftime('%d/%m/%Y'),
                    'hora': '10:00',
                    'paciente': 'Luis Ramírez',
                    'cirujano': 'Dr. Miguel Ángel Torres',
                    'tipo_cirugia': 'Artroscopía de Rodilla',
                    'materiales': [{'id': 13, 'nombre': 'Prótesis Rodilla Total', 'categoria': 'Ortopedia'}],
                    'monto': 1500.00
                }
            )
            db.session.add(ticket1)
            visita3.ticket_generado = True
            visita3.ticket_id = ticket1.id
            print("✅ Ticket 1 creado: PENDIENTE $1,500 - Artroscopía de Rodilla")
        
        # Ticket 2: Pendiente para visita 4
        if not Ticket.query.filter_by(numero='TKT-20261021-002').first():
            ticket2 = Ticket(
                usuario_id=promotor1.id,
                visita_id=visita4.id,
                numero='TKT-20261021-002',
                monto=3200.00,
                estado='pendiente',
                descripcion='Ticket de cobro por visita a Hospital General de Querétaro - Revascularización Coronaria',
                detalle={
                    'visita_id': visita4.id,
                    'hospital': 'Hospital General de Querétaro',
                    'promotor': 'Carlos Mendoza',
                    'fecha': ayer.strftime('%d/%m/%Y'),
                    'hora': '16:00',
                    'paciente': 'Carmen Flores',
                    'cirujano': 'Dra. Laura Jiménez',
                    'tipo_cirugia': 'Revascularización Coronaria',
                    'materiales': [
                        {'id': 18, 'nombre': 'Stent Coronario Drug-Eluting', 'categoria': 'Cardiología'},
                        {'id': 19, 'nombre': 'Balón Angioplastía', 'categoria': 'Cardiología'}
                    ],
                    'monto': 3200.00
                }
            )
            db.session.add(ticket2)
            visita4.ticket_generado = True
            visita4.ticket_id = ticket2.id
            print("✅ Ticket 2 creado: PENDIENTE $3,200 - Revascularización Coronaria")
        
        db.session.commit()
        
        # ============================================================
        # 4. CREAR TICKETS DE HISTORIAL (ya pagados y aprobados)
        # ============================================================
        
        # Ticket 3: Pagado
        if not Ticket.query.filter_by(numero='TKT-20261015-001').first():
            ticket3 = Ticket(
                usuario_id=promotor1.id,
                visita_id=None,
                numero='TKT-20261015-001',
                monto=4500.00,
                estado='pagado',
                descripcion='Ticket de cobro por visita a Hospital Ángeles Querétaro - Hernioplastía con Malla',
                detalle={
                    'hospital': 'Hospital Ángeles Querétaro',
                    'promotor': 'Carlos Mendoza',
                    'fecha': '15/10/2026',
                    'hora': '09:00',
                    'paciente': 'Roberto Luna',
                    'cirujano': 'Dr. Sánchez',
                    'tipo_cirugia': 'Hernioplastía con Malla',
                    'monto': 4500.00
                },
                fecha_aprobacion=datetime(2026, 10, 16, 10, 0),
                fecha_pago=datetime(2026, 10, 17, 14, 0),
                aprobado_por=1,  # admin
                pagado_por=1,  # admin
                metodo_pago='transferencia',
                referencia_pago='TRF-20261017-001'
            )
            db.session.add(ticket3)
            print("✅ Ticket 3 creado: PAGADO $4,500 - Hernioplastía con Malla")
        
        # Ticket 4: Pagado
        if not Ticket.query.filter_by(numero='TKT-20261010-001').first():
            ticket4 = Ticket(
                usuario_id=promotor2.id,
                visita_id=None,
                numero='TKT-20261010-001',
                monto=2100.00,
                estado='pagado',
                descripcion='Ticket de cobro por visita a Star Médica Querétaro - Colecistectomía Laparoscópica',
                detalle={
                    'hospital': 'Star Médica Querétaro',
                    'promotor': 'Ana López',
                    'fecha': '10/10/2026',
                    'hora': '14:00',
                    'paciente': 'Diana Ruiz',
                    'cirujano': 'Dra. Vega',
                    'tipo_cirugia': 'Colecistectomía Laparoscópica',
                    'monto': 2100.00
                },
                fecha_aprobacion=datetime(2026, 10, 11, 9, 0),
                fecha_pago=datetime(2026, 10, 12, 16, 0),
                aprobado_por=1,
                pagado_por=1,
                metodo_pago='transferencia',
                referencia_pago='TRF-20261012-002'
            )
            db.session.add(ticket4)
            print("✅ Ticket 4 creado: PAGADO $2,100 - Colecistectomía Laparoscópica")
        
        # Ticket 5: Aprobado (pendiente de pago)
        if not Ticket.query.filter_by(numero='TKT-20261018-001').first():
            ticket5 = Ticket(
                usuario_id=promotor1.id,
                visita_id=None,
                numero='TKT-20261018-001',
                monto=2800.00,
                estado='aprobado',
                descripcion='Ticket de cobro por visita a Hospital San José del Carmen - Artroscopía de Hombro',
                detalle={
                    'hospital': 'Hospital San José del Carmen',
                    'promotor': 'Carlos Mendoza',
                    'fecha': '18/10/2026',
                    'hora': '10:00',
                    'paciente': 'Alberto Núñez',
                    'cirujano': 'Dr. Torres',
                    'tipo_cirugia': 'Artroscopía de Hombro',
                    'monto': 2800.00
                },
                fecha_aprobacion=datetime(2026, 10, 19, 11, 0),
                aprobado_por=1
            )
            db.session.add(ticket5)
            print("✅ Ticket 5 creado: APROBADO $2,800 - Artroscopía de Hombro")
        
        db.session.commit()
        
        print("\n🎉 Datos de prueba creados exitosamente!")
        print("\n👤 Usuarios de prueba:")
        print("   • carlos.mendoza@promocir.com / promotor123 (Promotor)")
        print("   • ana.lopez@promocir.com / promotor123 (Promotor)")
        print("\n📊 Resumen:")
        print(f"   • {Visita.query.count()} visitas creadas")
        print(f"   • {Ticket.query.count()} tickets creados")
        print(f"   • {Ticket.query.filter_by(estado='pendiente').count()} tickets pendientes")
        print(f"   • {Ticket.query.filter_by(estado='aprobado').count()} tickets aprobados")
        print(f"   • {Ticket.query.filter_by(estado='pagado').count()} tickets pagados")

if __name__ == '__main__':
    crear_datos_prueba()
