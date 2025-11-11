from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session
)
from operacionesCRUD import registrar_usuario, iniciar_sesion

# 
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates' 
)

@auth_bp.route("/")
def index():
    if 'user_id' in session and session.get('user_role') == 'admin':
        return redirect(url_for('admin_bp.admin_dashboard'))
    return render_template("InicioSesion.html")


@auth_bp.route("/login", methods=["POST"])
def procesar_login():
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    
    usuario = iniciar_sesion(nombre, email, password)
    
    if usuario:
        session['user_id'] = str(usuario['_id'])
        session['user_name'] = usuario['name']
        session['user_role'] = usuario.get('role', 'user')
        
        if session['user_role'] == 'admin':
            flash(f"¡Bienvenido de vuelta, {usuario['name']}!", "success")
            return redirect(url_for('admin_bp.admin_dashboard'))
        else:
            session.pop('user_id', None)
            session.pop('user_name', None)
            session.pop('user_role', None)
            flash("Esta sección es solo para administradores.", "error")
            return redirect(url_for('auth_bp.index'))
    else:
        flash("Error: Nombre, email o contraseña incorrectos.")
        return redirect(url_for('auth_bp.index'))


@auth_bp.route("/registro", methods=["GET"])
def mostrar_registro():
    return render_template("Registro.html")


@auth_bp.route("/procesar_registro", methods=["POST"])
def procesar_registro():
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']

    resultado = registrar_usuario(nombre, email, password)
    
    if isinstance(resultado, str):
        flash(resultado)
        return redirect(url_for('auth_bp.mostrar_registro'))
    else:
        flash("Registro exitoso. Ya puedes iniciar sesión.")
        return redirect(url_for('auth_bp.index'))

@auth_bp.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    flash("Vuelve pronto!!!")
    return redirect(url_for('auth_bp.index'))