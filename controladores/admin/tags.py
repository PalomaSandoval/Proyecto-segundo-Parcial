from flask import render_template, request, redirect, url_for, flash, session
from . import admin_bp, limpiar_sesion_y_redirigir
from operacionesCRUD import (
    obtener_todos_tags,
    crear_tag,
    obtener_tag_por_id,
    editar_tag,
    eliminar_tag
)

# Ruta real: /admin/tags
@admin_bp.route("/tags")
def admin_mostrar_tags():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    try:
        lista_tags = obtener_todos_tags()
    except Exception as e:
        flash(f"Error al cargar tags: {e}", "error")
        lista_tags = []
    
    return render_template(
        "admin_tags.html", 
        tags=lista_tags,
        active_page="tags" # Para el menú
    )

# Ruta real: /admin/tag/crear (Esta misma ruta maneja el POST)
@admin_bp.route("/tag/crear", methods=["POST"])
def admin_crear_tag():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('admin_bp.admin_mostrar_tags'))

    nombre_tag = request.form.get('nombre_tag')
    
    if not nombre_tag:
        flash("No puedes crear un tag sin nombre.", "error")
        return redirect(url_for('admin_bp.admin_mostrar_tags'))

    resultado = crear_tag(nombre_tag)
    
    if isinstance(resultado, str): #  un texto, es un error
        flash(resultado, "error")
    else:
        flash("Tag nuevo creado.", "success")
    
    return redirect(url_for('admin_bp.admin_mostrar_tags'))


# Ruta real: /admin/tag/editar/ID...
@admin_bp.route("/tag/editar/<tag_id_str>", methods=["GET", "POST"])
def admin_editar_tag_ruta(tag_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    if request.method == "POST":
        nuevo_nombre = request.form.get('nombre')
        
        if not nuevo_nombre:
            flash("El nombre no puede estar vacío.", "error")
            return redirect(url_for('admin_bp.admin_editar_tag_ruta', tag_id_str=tag_id_str))

        if editar_tag(tag_id_str, nuevo_nombre):
            flash("Tag actualizado con éxito.", "success")
        else:
            flash("No se pudo actualizar el tag", "error")
        
        return redirect(url_for('admin_bp.admin_mostrar_tags'))

    # Si es GET
    tag = obtener_tag_por_id(tag_id_str)
    if not tag:
        flash("No se encontró ese tag.", "error")
        return redirect(url_for('admin_bp.admin_mostrar_tags'))

    return render_template(
        "admin_editar_tag.html",
        tag=tag,
        active_page="tags"
    )

# Ruta real: /admin/tag/eliminar/ID...
@admin_bp.route("/tag/eliminar/<tag_id_str>", methods=["POST"])
def admin_eliminar_tag_ruta(tag_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()
        
    if eliminar_tag(tag_id_str):
        flash("Tag eliminado. También se quitó de todos los artículos.", "success")
    else:
        flash("No se pudo eliminar el tag.", "error")
    
    return redirect(url_for('admin_bp.admin_mostrar_tags'))