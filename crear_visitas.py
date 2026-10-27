from app import create_app
from app.models import db, Hospital, Material, Usuario, Visita
from datetime import datetime, timedelta, time

app = create_app()
with app.app_context():
    # Obtener hospitales y promotores existentes
    hospitales = Hospital.query.filter_by(activo=True).all()
    promotores = [u for u in Usuario.query.all() if not u.es_admin()]
    materiales = Material.query.filter_by(activo=True).all()
    
    if not hospitales:
        print('No hay hospitales activos')
        exit()
    if not promotores:
        print('No hay promotores')
        exit()
    
    print(f'Hospitales: {len(hospitales)}')
    print(f'Promotores: {len(promotores)}')
    print(f'Materiales: {len(materiales)}')
    
    # Crear visita DIRECTA (asignada a promotor)
    v1 = Visita(
        usuario_id=promotores[0].id,
        hospital_id=hospitales[0].id,
        paciente_nombre='Paciente Prueba Directa',
        paciente_edad=45,
        cirujano_nombre='Dr. Prueba',
        cirujano_especialidad='Cirugia General',
        tipo_cirugia='Hernioplastia con Malla',
        materiales_ofrecidos=[{'nombre': 'Malla Prolene', 'categoria': 'Malla'}],
        fecha=datetime.now().date() + timedelta(days=2),
        hora_inicio=time(9, 0),
        hora_fin=time(11, 0),
        duracion_estimada=120,
        costo_visita=2500,
        estado='programada',
        modo_asignacion='directo'
    )
    db.session.add(v1)
    
    # Crear visita OFERTA (sin promotor asignado)
    v2 = Visita(
        usuario_id=None,
        hospital_id=hospitales[1].id if len(hospitales) > 1 else hospitales[0].id,
        paciente_nombre='Paciente Prueba Oferta',
        paciente_edad=60,
        cirujano_nombre='Dra. Oferta',
        cirujano_especialidad='Ortopedia',
        tipo_cirugia='Artroscopia de Rodilla',
        materiales_ofrecidos=[{'nombre': 'Tornillos Canulados', 'categoria': 'Traumatologia'}],
        fecha=datetime.now().date() + timedelta(days=3),
        hora_inicio=time(14, 0),
        hora_fin=time(16, 0),
        duracion_estimada=120,
        costo_visita=3200,
        estado='oferta',
        modo_asignacion='oferta'
    )
    db.session.add(v2)
    
    # Crear otra visita OFERTA
    v3 = Visita(
        usuario_id=None,
        hospital_id=hospitales[0].id,
        paciente_nombre='Paciente Prueba Oferta 2',
        paciente_edad=35,
        cirujano_nombre='Dr. Oferta 2',
        cirujano_especialidad='Cirugia General',
        tipo_cirugia='Colecistectomia',
        materiales_ofrecidos=[{'nombre': 'Endograb', 'categoria': 'Laparoscopia'}],
        fecha=datetime.now().date() + timedelta(days=4),
        hora_inicio=time(10, 0),
        hora_fin=time(12, 0),
        duracion_estimada=120,
        costo_visita=2800,
        estado='oferta',
        modo_asignacion='oferta'
    )
    db.session.add(v3)
    
    db.session.commit()
    print(f'\nVisitas creadas:')
    print(f'  V1 (directa): ID={v1.id}, estado={v1.estado}')
    print(f'  V2 (oferta): ID={v2.id}, estado={v2.estado}')
    print(f'  V3 (oferta): ID={v3.id}, estado={v3.estado}')
