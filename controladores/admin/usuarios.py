from flask import render_template, request, redirect, url_for, flash, session
from . import admin_bp, limpiar_sesion_y_redirigir

from operacionesCRUD import obtener_todos_usuarios, eliminar_usuario

# Ruta real: /admin/usuarios
@admin_bp.route("/usuarios")
def admin_mostrar_usuarios():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    try:
        lista_usuarios = obtener_todos_usuarios()
    except Exception as e:
        flash(f"Error al cargar usuarios: {e}")
        lista_usuarios = []
    
    return render_template(
        "admin_usuarios.html", 
        usuarios=lista_usuarios,
        active_page="usuarios"
    )


@admin_bp.route("/usuario/eliminar/<user_id_str>", methods=["POST"])
def admin_eliminar_usuario(user_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()
        
    if user_id_str == session['user_id']:
        flash("No se puede eliminar este mismo usuario", "error")
        return redirect(url_for('admin_bp.admin_mostrar_usuarios'))

    if eliminar_usuario(user_id_str):
        flash("Usuario eliminado con éxito.", "success")
    else:
        flash("No se pudo eliminar al usuario.", "error")
    
    return redirect(url_for('admin_bp.admin_mostrar_usuarios'))