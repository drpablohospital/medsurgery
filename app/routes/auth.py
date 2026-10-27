from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.models import db, Usuario
from app.utils.decorators import admin_required

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email y contraseña son requeridos.', 'warning')
            return render_template('login.html')
        
        user = Usuario.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.activo:
            login_user(user, remember=True)
            flash(f'Bienvenido, {user.nombre}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Email o contraseña incorrectos.', 'danger')
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/registro', methods=['GET', 'POST'])
@admin_required
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        tipo = request.form.get('tipo', 'promotor')
        telefono = request.form.get('telefono', '').strip()
        region_asignada = request.form.get('region_asignada', '').strip()
        
        if not nombre or not email or not password:
            flash('Nombre, email y contraseña son requeridos.', 'warning')
            return render_template('registro.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'warning')
            return render_template('registro.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email ya está registrado.', 'danger')
            return render_template('registro.html')
        
        user = Usuario(
            nombre=nombre,
            email=email,
            tipo=tipo,
            telefono=telefono,
            region_asignada=region_asignada
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Usuario {nombre} registrado correctamente.', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('registro.html')
