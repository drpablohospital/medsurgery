from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='promotor')
    telefono = db.Column(db.String(50))
    region_asignada = db.Column(db.String(100))
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    visitas = db.relationship('Visita', backref='promotor', lazy='dynamic')
    tickets = db.relationship('Ticket', backref='promotor', lazy='dynamic', foreign_keys='Ticket.usuario_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def es_admin(self):
        return self.tipo == 'admin'
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Hospital(db.Model):
    __tablename__ = 'hospitales'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    direccion = db.Column(db.Text)
    ciudad = db.Column(db.String(100), default='Queretaro')
    estado = db.Column(db.String(100), default='Queretaro')
    telefono = db.Column(db.String(50))
    contacto_nombre = db.Column(db.String(150))
    contacto_email = db.Column(db.String(255))
    contacto_telefono = db.Column(db.String(50))
    tipo = db.Column(db.String(50), default='privado')
    latitud = db.Column(db.Numeric(10, 8))
    longitud = db.Column(db.Numeric(11, 8))
    activo = db.Column(db.Boolean, nullable=False, default=True)
    notas = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    # Relaciones
    visitas = db.relationship('Visita', backref='hospital', lazy='dynamic')
    
    def __repr__(self):
        return f'<Hospital {self.nombre}>'

class Material(db.Model):
    __tablename__ = 'materiales'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    costo_referencia = db.Column(db.Numeric(10, 2), default=0.00)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Material {self.nombre}>'

class Visita(db.Model):
    __tablename__ = 'visitas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitales.id'), nullable=False)
    
    # Datos del paciente y cirujano (conservados de QuiroCir)
    paciente_nombre = db.Column(db.String(200))
    paciente_edad = db.Column(db.Integer)
    cirujano_nombre = db.Column(db.String(200))
    cirujano_especialidad = db.Column(db.String(100))
    
    # Tipo de cirugía
    tipo_cirugia = db.Column(db.String(200))
    
    # Materiales ofrecidos
    materiales_ofrecidos = db.Column(db.JSON)
    
    # Fecha y hora de la visita
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    duracion_estimada = db.Column(db.Integer, nullable=False)
    
    # Costo que cobra el promotor por esta visita
    costo_visita = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    
    # Estado de la visita
    estado = db.Column(db.String(20), nullable=False, default='programada')
    # Estados: programada, confirmada, realizada, cancelada, no_show
    
    # Especificaciones y notas
    especificaciones = db.Column(db.Text)
    notas_seguimiento = db.Column(db.Text)
    
    # Ticket asociado
    ticket_generado = db.Column(db.Boolean, nullable=False, default=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=True)
    
    # Modo de asignacion: 'directo' (admin asigna promotor) o 'oferta' (promotores se postulan)
    modo_asignacion = db.Column(db.String(20), nullable=False, default='directo')
    
    # Datos adicionales (ventas, etc.)
    detalle = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_hora_inicio_str(self):
        return self.hora_inicio.strftime('%H:%M') if self.hora_inicio else ''
    
    def get_hora_fin_str(self):
        return self.hora_fin.strftime('%H:%M') if self.hora_fin else ''
    
    def get_fecha_str(self):
        return self.fecha.strftime('%d/%m/%Y') if self.fecha else ''
    
    def __repr__(self):
        return f'<Visita {self.id} - {self.hospital.nombre}>'

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    visita_id = db.Column(db.Integer, db.ForeignKey('visitas.id'), nullable=True)
    
    numero = db.Column(db.String(50), unique=True, nullable=False)
    
    # Monto que el promotor cobra
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Estado del ticket
    estado = db.Column(db.String(20), nullable=False, default='pendiente')
    # Estados: pendiente, aprobado, pagado, rechazado, cerrado_por_promotor, cobrado
    
    # Descripción y detalle
    descripcion = db.Column(db.Text)
    detalle = db.Column(db.JSON)
    materiales_vendidos = db.Column(db.JSON)
    
    # Ej: [{"id": 1, "nombre": "Mesh", "cantidad": 2, "precio_venta": 1500.00}]

    # Fechas de procesamiento
    fecha_aprobacion = db.Column(db.DateTime(timezone=True))
    fecha_pago = db.Column(db.DateTime(timezone=True))
    fecha_cobro = db.Column(db.DateTime(timezone=True))
    
    # Quién aprobó y pagó
    aprobado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    pagado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Método de pago
    metodo_pago = db.Column(db.String(50), default='transferencia')
    
    # Referencia de pago
    referencia_pago = db.Column(db.String(100))
    
    # Cierre por promotor
    fecha_cierre_promotor = db.Column(db.DateTime(timezone=True))
    factura_url = db.Column(db.String(255))  # Path al archivo de factura adjunto
    notas_cierre = db.Column(db.Text)  # Notas del promotor al cerrar
    
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    # Relaciones
    visita = db.relationship("Visita", backref="ticket", lazy=True, foreign_keys=[visita_id])
    usuario = db.relationship(Usuario, foreign_keys=[usuario_id], lazy=True)
    aprobador = db.relationship(Usuario, foreign_keys=[aprobado_por], lazy=True)
    pagador = db.relationship('Usuario', foreign_keys=[pagado_por], lazy=True)
    
    def __repr__(self):
        return f'<Ticket {self.numero}>'
