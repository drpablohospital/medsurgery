"""
Seed data para Render: Hospitales de Querétaro
Ejecutar en consola de Render
"""
import os
import sys

# Configurar DATABASE_URL desde variable de entorno de Render
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL')

sys.path.insert(0, '/opt/render/project/src')

from app import create_app, db
from app.models import Hospital

HOSPITALES_QUERETARO = [
    {"nombre": "Hospital Ángeles Querétaro", "direccion": "Av. Tecnológico No. 200, Centro Sur", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 238 8000", "contacto_nombre": "Coordinación de Compras", "tipo": "privado", "notas": "Cadena Angeles, principal hospital privado de la ciudad. Excelente relación con cirugía laparoscópica.", "activo": True},
    {"nombre": "Hospital Star Médica Querétaro", "direccion": "Paseo de la República 13007, Juriquilla", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 500 4000", "contacto_nombre": "Gerente de Suministros", "tipo": "privado", "notas": "Grupo Star Médica, equipamiento moderno. Potencial para ortopedia y neurocirugía.", "activo": True},
    {"nombre": "Hospital San José del Carmen", "direccion": "Av. Constituyentes 1000, Carretas", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 238 1100", "contacto_nombre": "Jefe de Cirugía", "tipo": "privado", "notas": "Hospital tradicional, buena relación con cirugía general y oncológica.", "activo": True},
    {"nombre": "Hospital Santiago de Querétaro", "direccion": "Calle Allende Sur 108, Centro Histórico", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 212 0700", "contacto_nombre": "Director Médico", "tipo": "privado", "notas": "Centro Histórico. Hospital antiguo con buena trayectoria.", "activo": True},
    {"nombre": "Hospital General de Querétaro (ISSSTE)", "direccion": "Av. 5 de Febrero 1300, Centro", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 238 0900", "contacto_nombre": "Coordinación de Área Quirúrgica", "tipo": "publico", "notas": "ISSSTE. Hospital público con alto volumen de cirugías.", "activo": True},
    {"nombre": "Hospital General Regional No. 1 (IMSS)", "direccion": "Av. Universidad s/n, Centro", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 238 2000", "contacto_nombre": "Jefe de Cirugía", "tipo": "publico", "notas": "IMSS. Alto volumen, buena oportunidad para demostraciones de equipos.", "activo": True},
    {"nombre": "Hospital Sanatorio del Carmen", "direccion": "Av. 5 de Febrero 1100, Centro", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 212 1500", "contacto_nombre": "Administración", "tipo": "privado", "notas": "Hospital privado tradicional. Buena relación con cirugía plástica y reconstructiva.", "activo": True},
    {"nombre": "Hospital del Rio", "direccion": "Av. Constituyentes 1400, Carretas", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 500 7000", "contacto_nombre": "Jefe de Adquisiciones", "tipo": "privado", "notas": "Hospital privado moderno. Buen potencial para tecnología avanzada.", "activo": True},
    {"nombre": "Hospital Médica Sur Querétaro", "direccion": "Carretera a Chichimequillas km 1.5, Jurica", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 500 5000", "contacto_nombre": "Gerente Comercial", "tipo": "privado", "notas": "Cadena Médica Sur. Alta exigencia de calidad. Oportunidad premium.", "activo": True},
    {"nombre": "Hospital Cruz Roja Mexicana Delegación Querétaro", "direccion": "Av. Tecnológico 100, Centro Sur", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 238 4400", "contacto_nombre": "Coordinador de Área Quirúrgica", "tipo": "publico", "notas": "Cruz Roja. Emergencias y trauma. Buena oportunidad para equipos de emergencia.", "activo": True},
    {"nombre": "Hospital Santa Rosa", "direccion": "Av. Corregidora 100, Centro", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 212 0500", "contacto_nombre": "Dirección Médica", "tipo": "privado", "notas": "Hospital privado centenario. Tradición y prestigio en la ciudad.", "activo": True},
    {"nombre": "Hospital Real de San José", "direccion": "Calle 16 de Septiembre 100, Centro", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 212 2200", "contacto_nombre": "Gerencia", "tipo": "privado", "notas": "Hospital privado boutique. Servicio personalizado.", "activo": True},
    {"nombre": "Hospital San Javier", "direccion": "Paseo de la República 15000, Juriquilla", "ciudad": "Querétaro", "estado": "Querétaro", "telefono": "442 500 6000", "contacto_nombre": "Coordinación Quirúrgica", "tipo": "privado", "notas": "Hospital privado en Juriquilla. Moderno y bien equipado.", "activo": True},
]

def seed_hospitales():
    app = create_app()
    with app.app_context():
        # Verificar si ya existen
        existing = Hospital.query.first()
        if existing:
            print("Ya existen hospitales en la BD. Saltando seed.")
            return
        
        for data in HOSPITALES_QUERETARO:
            hospital = Hospital(**data)
            db.session.add(hospital)
        
        db.session.commit()
        print(f"✅ {len(HOSPITALES_QUERETARO)} hospitales de Querétaro insertados correctamente.")

if __name__ == '__main__':
    seed_hospitales()
