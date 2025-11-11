from flask import render_template, request, redirect, url_for, flash, session
from . import admin_bp, limpiar_sesion_y_redirigir
from operacionesCRUD import (
    obtener_todos_comentarios,
    eliminar_comentario_individual
)


@admin_bp.route("/comentarios")
def admin_mostrar_comentarios():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    try:
        lista_comentarios = obtener_todos_comentarios()
    except Exception as e:
        flash(f"Error al cargar comentarios: {e}", "error")
        lista_comentarios = []
    
    return render_template(
        "admin_comentarios.html", 
        comentarios=lista_comentarios,
        active_page="comentarios" # 
    )


# Ruta real: /admin/comentario/eliminar/ID...
@admin_bp.route("/comentario/eliminar/<comment_id_str>", methods=["POST"])
def admin_eliminar_comentario_ruta(comment_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()
        
    if eliminar_comentario_individual(comment_id_str):
        flash("Comentario eliminado con éxito.", "success")
    else:
        flash("No se pudo eliminar el comentario.", "error")
    
    return redirect(url_for('admin_bp.admin_mostrar_comentarios'))


