"""
Seed data para Render: Materiales quirúrgicos Med Surgery Mexico
Precios basados en mercado médico mexicano 2024-2025 (MXN)
Ejecutar en consola de Render: python3 database/seed_materiales.py
"""
import os
import sys

sys.path.insert(0, '/opt/render/project/src')

from app import create_app, db
from app.models import Material

# Precios en MXN basados en mercado médico mexicano
MATERIALES_MED_SURGERY = [
    # Neurocirugía
    {"nombre": "Craniotomo eléctrico", "categoria": "Neurocirugía", "descripcion": "Sistema de craniotomía de alta velocidad con control de torque", "precio_referencia": 285000, "unidad": "pieza", "activo": True},
    {"nombre": "Sistema de navegación quirúrgica", "categoria": "Neurocirugía", "descripcion": "Navegación intraoperatoria 3D para cirugía craneal y espinal", "precio_referencia": 1250000, "unidad": "sistema", "activo": True},
    {"nombre": "Distractor craneal", "categoria": "Neurocirugía", "descripcion": "Sistema de distracción osteogénesis craneal", "precio_referencia": 45000, "unidad": "pieza", "activo": True},
    {"nombre": "Microscopio quirúrgico", "categoria": "Neurocirugía", "descripcion": "Microscopio con iluminación LED y grabación 4K", "precio_referencia": 1850000, "unidad": "sistema", "activo": True},
    {"nombre": "Sistema de neuroendoscopia", "categoria": "Neurocirugía", "descripcion": "Endoscopio rígido con cámara HD para cirugía mínimamente invasiva", "precio_referencia": 320000, "unidad": "sistema", "activo": True},
    {"nombre": "Drenaje ventricular externo (DVE)", "categoria": "Neurocirugía", "descripcion": "Kit completo de drenaje ventricular con monitor de presión", "precio_referencia": 8500, "unidad": "kit", "activo": True},
    {"nombre": "Clips para aneurismas", "categoria": "Neurocirugía", "descripcion": "Clips de titanio para obliteración de aneurismas cerebrales", "precio_referencia": 15000, "unidad": "pieza", "activo": True},
    {"nombre": "Shunt ventriculoperitoneal", "categoria": "Neurocirugía", "descripcion": "Sistema de derivación con válvula programable", "precio_referencia": 35000, "unidad": "sistema", "activo": True},
    {"nombre": "Sistema de fijación craneal", "categoria": "Neurocirugía", "descripcion": "Tornillos y placas de titanio para reconstrucción craneal", "precio_referencia": 22000, "unidad": "kit", "activo": True},
    {"nombre": "Taladro craneal", "categoria": "Neurocirugía", "descripcion": "Taladro quirúrgico con brocas diamantadas", "precio_referencia": 180000, "unidad": "sistema", "activo": True},
    
    # Columna
    {"nombre": "Jaula intervertebral (cage)", "categoria": "Columna", "descripcion": "Cage de PEEK con plataforma de fusión ósea", "precio_referencia": 28000, "unidad": "pieza", "activo": True},
    {"nombre": "Disco artificial cervical", "categoria": "Columna", "descripcion": "Prótesis de disco con núcleo de polietileno", "precio_referencia": 45000, "unidad": "pieza", "activo": True},
    {"nombre": "Sistema de estabilización pedicle screw", "categoria": "Columna", "descripcion": "Tornillos pediculares con barras conectoras", "precio_referencia": 55000, "unidad": "kit", "activo": True},
    {"nombre": "Placa anterior cervical", "categoria": "Columna", "descripcion": "Placa de titanio con tornillos de bloqueo", "precio_referencia": 18000, "unidad": "pieza", "activo": True},
    {"nombre": "Dispositivo de fusión intervertebral TLIF/PLIF", "categoria": "Columna", "descripcion": "Cage con jaula de fusión para vía transforminal", "precio_referencia": 32000, "unidad": "pieza", "activo": True},
    {"nombre": "Caja de fusión PEEK", "categoria": "Columna", "descripcion": "Caja espaciadora con osteoconductividad", "precio_referencia": 24000, "unidad": "pieza", "activo": True},
    {"nombre": "Sistema de drenaje epidural", "categoria": "Columna", "descripcion": "Catéter epidural con puerto subcutáneo", "precio_referencia": 12000, "unidad": "kit", "activo": True},
    {"nombre": "Sistema de fijación occipitocervical", "categoria": "Columna", "descripcion": "Placa occipital con barras y tornillos C1-C2", "precio_referencia": 85000, "unidad": "kit", "activo": True},
    
    # Trauma y Ortopedia
    {"nombre": "Clavo endomedular", "categoria": "Trauma y Ortopedia", "descripcion": "Clavo tibial/femoral con bloqueo proximal y distal", "precio_referencia": 22000, "unidad": "pieza", "activo": True},
    {"nombre": "Placa de bloqueo", "categoria": "Trauma y Ortopedia", "descripcion": "Placa de titanio con agujos combi", "precio_referencia": 15000, "unidad": "pieza", "activo": True},
    {"nombre": "Sistema de fijación externa", "categoria": "Trauma y Ortopedia", "descripcion": "Fijador externo modular con pinzas radiotransparentes", "precio_referencia": 85000, "unidad": "sistema", "activo": True},
    {"nombre": "Tornillo canulado", "categoria": "Trauma y Ortopedia", "descripcion": "Tornillo autorroscante canulado de titanio", "precio_referencia": 3500, "unidad": "pieza", "activo": True},
    {"nombre": "Sistema de fijación maxilofacial", "categoria": "Trauma y Ortopedia", "descripcion": "Placas y tornillos de 1.5mm para fracturas faciales", "precio_referencia": 18000, "unidad": "kit", "activo": True},
    {"nombre": "Implante para fractura de cadera", "categoria": "Trauma y Ortopedia", "descripcion": "Sistema DHS/DCS con placa y tornillos", "precio_referencia": 28000, "unidad": "kit", "activo": True},
    {"nombre": "Clavo Gamma", "categoria": "Trauma y Ortopedia", "descripcion": "Clajo intramedular para fracturas subtrocantéricas", "precio_referencia": 35000, "unidad": "pieza", "activo": True},
    {"nombre": "Sistema de fijación pelviana", "categoria": "Trauma y Ortopedia", "descripcion": "Placas anatómicas con tornillos de 3.5mm", "precio_referencia": 42000, "unidad": "kit", "activo": True},
    {"nombre": "Drenaje para hematoma subdural", "categoria": "Trauma y Ortopedia", "descripcion": "Kit de drenaje con catéter de doble lumen", "precio_referencia": 8500, "unidad": "kit", "activo": True},
    
    # Equipo quirúrgico
    {"nombre": "Electrobisturí", "categoria": "Equipo", "descripcion": "Generador de alta frecuencia con retorno de neutro", "precio_referencia": 185000, "unidad": "sistema", "activo": True},
    {"nombre": "Sistema de endoscopia", "categoria": "Equipo", "descripcion": "Torre endoscópica con fuente de luz LED y cámara HD", "precio_referencia": 450000, "unidad": "torre", "activo": True},
    {"nombre": "Equipo de fluoroscopia", "categoria": "Equipo", "descripcion": "Arco en C con pantalla plana digital", "precio_referencia": 2500000, "unidad": "sistema", "activo": True},
    {"nombre": "Mesa quirúrgica", "categoria": "Equipo", "descripcion": "Mesa hidráulica con radiotransparencia total", "precio_referencia": 385000, "unidad": "pieza", "activo": True},
    {"nombre": "Sistema de aspiración", "categoria": "Equipo", "descripcion": "Aspirador quirúrgico de alto vacío", "precio_referencia": 45000, "unidad": "sistema", "activo": True},
    {"nombre": "Torre de artroscopia", "categoria": "Equipo", "descripcion": "Sistema completo con cámara, shaver y fuente de luz", "precio_referencia": 650000, "unidad": "torre", "activo": True},
    {"nombre": "Sistema de estereotaxia", "categoria": "Equipo", "descripcion": "Marco estereotáctico con planificación 3D", "precio_referencia": 280000, "unidad": "sistema", "activo": True},
]


def seed_materiales():
    app = create_app()
    with app.app_context():
        # Verificar si ya existen
        existing = Material.query.first()
        if existing:
            print("Ya existen materiales en la BD. Saltando seed.")
            return
        
        for data in MATERIALES_MED_SURGERY:
            material = Material(**data)
            db.session.add(material)
        
        db.session.commit()
        print(f"✅ {len(MATERIALES_MED_SURGERY)} materiales de Med Surgery insertados correctamente.")


if __name__ == '__main__':
    seed_materiales()
