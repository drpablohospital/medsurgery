"""
Seed data: Hospitales privados más famosos del estado de Querétaro
para el CRM de promotores médicos PromoCir.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Agregar directorio padre al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import Hospital

HOSPITALES_QUERETARO = [
    {
        "nombre": "Hospital Ángeles Querétaro",
        "direccion": "Av. Tecnológico No. 200, Centro Sur",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 8000",
        "contacto_nombre": "Coordinación de Compras",
        "tipo": "privado",
        "notas": "Cadena Angeles, principal hospital privado de la ciudad. Excelente relación con cirugía laparoscópica."
    },
    {
        "nombre": "Hospital Star Médica Querétaro",
        "direccion": "Paseo de la República 13007, Juriquilla",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 500 4000",
        "contacto_nombre": "Gerente de Suministros",
        "tipo": "privado",
        "notas": "Grupo Star Médica, equipamiento moderno. Potencial para ortopedia y neurocirugía."
    },
    {
        "nombre": "Hospital San José del Carmen",
        "direccion": "Av. Constituyentes 1000, Carretas",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 1100",
        "contacto_nombre": "Jefe de Cirugía",
        "tipo": "privado",
        "notas": "Hospital tradicional, buena relación con cirugía general y oncológica."
    },
    {
        "nombre": "Hospital Santiago de Querétaro",
        "direccion": "Calle Allende Sur 108, Centro Histórico",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 212 0700",
        "contacto_nombre": "Director Médico",
        "tipo": "privado",
        "notas": "Centro Histórico. Hospital antiguo con buena trayectoria."
    },
    {
        "nombre": "Hospital General de Querétaro (ISSSTE)",
        "direccion": "Av. 5 de Febrero 1300, Centro",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 0900",
        "contacto_nombre": "Coordinación de Área Quirúrgica",
        "tipo": "publico",
        "notas": "ISSSTE. Hospital público con alto volumen de cirugías. Proceso de licitación puede ser largo."
    },
    {
        "nombre": "Hospital General Regional No. 1 (IMSS)",
        "direccion": "Av. Universidad s/n, Centro",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 2000",
        "contacto_nombre": "Jefe de Cirugía",
        "tipo": "publico",
        "notas": "IMSS. Alto volumen, buena oportunidad para demostraciones de equipos."
    },
    {
        "nombre": "Hospital de Especialidades del Centro Médico Nacional La Raza (IMSS)",
        "direccion": "Av. Constituyentes s/n, Lomas del Marqués",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 3000",
        "contacto_nombre": "Subdirector Médico",
        "tipo": "publico",
        "notas": "IMSS especializado. Referencia regional."
    },
    {
        "nombre": "Hospital Sanatorio del Carmen",
        "direccion": "Av. 5 de Febrero 1100, Centro",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 212 1500",
        "contacto_nombre": "Administración",
        "tipo": "privado",
        "notas": "Hospital privado tradicional. Buena relación con cirugía plástica y reconstructiva."
    },
    {
        "nombre": "Hospital del Rio",
        "direccion": "Av. Constituyentes 1400, Carretas",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 500 7000",
        "contacto_nombre": "Jefe de Adquisiciones",
        "tipo": "privado",
        "notas": "Hospital privado moderno. Buen potencial para tecnología avanzada."
    },
    {
        "nombre": "Hospital Médica Sur Querétaro",
        "direccion": "Carretera a Chichimequillas km 1.5, Jurica",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 500 5000",
        "contacto_nombre": "Gerente Comercial",
        "tipo": "privado",
        "notas": "Cadena Médica Sur. Alta exigencia de calidad. Oportunidad premium."
    },
    {
        "nombre": "Hospital Cruz Roja Mexicana Delegación Querétaro",
        "direccion": "Av. Tecnológico 100, Centro Sur",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 4400",
        "contacto_nombre": "Coordinador de Área Quirúrgica",
        "tipo": "publico",
        "notas": "Cruz Roja. Emergencias y trauma. Buena oportunidad para equipos de emergencia."
    },
    {
        "nombre": "Hospital Santa Rosa",
        "direccion": "Av. Corregidora 100, Centro",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 212 0500",
        "contacto_nombre": "Dirección Médica",
        "tipo": "privado",
        "notas": "Hospital privado centenario. Tradición y prestigio en la ciudad."
    },
    {
        "nombre": "Hospital La Concepción",
        "direccion": "Calle 5 de Mayo 100, Centro",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 212 1800",
        "contacto_nombre": "Administración",
        "tipo": "privado",
        "notas": "Hospital privado tradicional. Buena ubicación en centro."
    },
    {
        "nombre": "Hospital San Juan de Dios",
        "direccion": "Av. Universidad 200, Centro",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 3300",
        "contacto_nombre": "Jefe de Cirugía",
        "tipo": "publico",
        "notas": "Hospital público. Alto volumen de pacientes."
    },
    {
        "nombre": "Hospital Universitario (UAQ)",
        "direccion": "Av. de las Ciencias S/N, Juriquilla",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 3500",
        "contacto_nombre": "Coordinador Académico",
        "tipo": "universitario",
        "notas": "Universidad Autónoma de Querétaro. Excelente para demostraciones y capacitación."
    },
    {
        "nombre": "Hospital Materno Infantil de Querétaro",
        "direccion": "Av. Tecnológico 500, Centro Sur",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 4500",
        "contacto_nombre": "Jefa de Gineco-Obstetricia",
        "tipo": "publico",
        "notas": "Especializado en gineco-obstetricia. Oportunidad para equipos especializados."
    },
    {
        "nombre": "Hospital de Especialidades del Niño y la Mujer",
        "direccion": "Av. Constituyentes 1800, Carretas",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 500 8000",
        "contacto_nombre": "Director Médico",
        "tipo": "publico",
        "notas": "Pediatría y ginecología. Nicho especializado."
    },
    {
        "nombre": "Hospital Real de San José",
        "direccion": "Calle 16 de Septiembre 100, Centro",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 212 2200",
        "contacto_nombre": "Gerencia",
        "tipo": "privado",
        "notas": "Hospital privado boutique. Servicio personalizado."
    },
    {
        "nombre": "Hospital San Javier",
        "direccion": "Paseo de la República 15000, Juriquilla",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 500 6000",
        "contacto_nombre": "Coordinación Quirúrgica",
        "tipo": "privado",
        "notas": "Hospital privado en Juriquilla. Moderno y bien equipado."
    },
    {
        "nombre": "Hospital CMQ Santiago",
        "direccion": "Av. Universidad 1500, Centro",
        "ciudad": "Querétaro",
        "estado": "Querétaro",
        "telefono": "442 238 5500",
        "contacto_nombre": "Jefe de Cirugía",
        "tipo": "privado",
        "notas": "Cadena CMQ. Buena cobertura en centro de la ciudad."
    },
]


def seed_hospitales():
    """Inserta los hospitales de Querétaro en la base de datos"""
    database_url = os.environ.get('DATABASE_URL') or \
        'postgresql+psycopg://promocir_app:promocir_secure_2026@localhost:5432/promocir'
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Verificar si ya existen hospitales
    existing = session.query(Hospital).first()
    if existing:
        print("Ya existen hospitales en la BD. Saltando seed.")
        return
    
    for data in HOSPITALES_QUERETARO:
        hospital = Hospital(**data)
        session.add(hospital)
    
    session.commit()
    print(f"✅ {len(HOSPITALES_QUERETARO)} hospitales de Querétaro insertados correctamente.")


if __name__ == '__main__':
    seed_hospitales()
