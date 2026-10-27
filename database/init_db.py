"""
Inicialización de la base de datos para PromoCir.
Crea las tablas y un usuario admin por defecto.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.models import db, Usuario, Hospital, Material
from sqlalchemy import inspect

def init_database():
    app = create_app('development')
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Crear tablas si no existen
        db.create_all()
        print("✅ Tablas creadas correctamente.")
        
        # Verificar si ya existe un admin
        admin = Usuario.query.filter_by(tipo='admin').first()
        if not admin:
            admin = Usuario(
                nombre='Administrador',
                email='admin@promocir.com',
                tipo='admin',
                telefono='4420000000',
                region_asignada='Todas'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin creado: admin@promocir.com / admin123")
        
        # Seed hospitales
        from seed_hospitales import seed_hospitales
        seed_hospitales()
        
        # Seed materiales
        materiales_existentes = Material.query.first()
        if not materiales_existentes:
            materiales_default = [
                Material(nombre="Stapler Circular Endoscópico", categoria="Laparoscopia", costo_referencia=25000),
                Material(nombre="Trocar 12mm", categoria="Laparoscopia", costo_referencia=1500),
                Material(nombre="Trocar 5mm", categoria="Laparoscopia", costo_referencia=1200),
                Material(nombre="Graspers Laparoscópicos", categoria="Laparoscopia", costo_referencia=8000),
                Material(nombre="Electrocauterio (Hook)", categoria="Laparoscopia", costo_referencia=3500),
                Material(nombre="Malla Prolén 15x20cm", categoria="Cirugía General", costo_referencia=4500),
                Material(nombre="Malla Ultrapro 10x15cm", categoria="Cirugía General", costo_referencia=5200),
                Material(nombre="Sutura Vicryl 2-0", categoria="Cirugía General", costo_referencia=180),
                Material(nombre="Sutura PDS 3-0", categoria="Cirugía General", costo_referencia=220),
                Material(nombre="Clip Quirúrgico (Titanio)", categoria="Cirugía General", costo_referencia=150),
                Material(nombre="Placa Osteosíntesis 4.5mm", categoria="Ortopedia", costo_referencia=8500),
                Material(nombre="Tornillo Canulado 6.5mm", categoria="Ortopedia", costo_referencia=3200),
                Material(nombre="Protesis Cadera Bipolar", categoria="Ortopedia", costo_referencia=45000),
                Material(nombre="Protesis Rodilla Total", categoria="Ortopedia", costo_referencia=65000),
                Material(nombre="Cauterio Bipolar", categoria="Neurocirugía", costo_referencia=15000),
                Material(nombre="Drenaje Ventricular", categoria="Neurocirugía", costo_referencia=8000),
                Material(nombre="Malla Cráneo 10x12cm", categoria="Neurocirugía", costo_referencia=25000),
                Material(nombre="Stent Coronario Drug-Eluting", categoria="Cardiología", costo_referencia=35000),
                Material(nombre="Balón Angioplastía", categoria="Cardiología", costo_referencia=18000),
                Material(nombre="Guía de Electrosucción", categoria="Laparoscopia", costo_referencia=6500),
                Material(nombre="Clip Laparoscópico (Hem-o-lok)", categoria="Laparoscopia", costo_referencia=250),
                Material(nombre="Endo GIA 60mm", categoria="Cirugía General", costo_referencia=12000),
                Material(nombre="Circular Stapler EEA 25mm", categoria="Cirugía General", costo_referencia=18000),
            ]
            
            for mat in materiales_default:
                db.session.add(mat)
            db.session.commit()
            print(f"✅ {len(materiales_default)} materiales insertados.")
        
        print("\n🎉 Base de datos inicializada correctamente!")
        print("   Admin: admin@promocir.com / admin123")

if __name__ == '__main__':
    init_database()
