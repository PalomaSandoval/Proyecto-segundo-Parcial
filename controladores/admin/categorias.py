
from flask import render_template, request, redirect, url_for, flash, session
from . import admin_bp, limpiar_sesion_y_redirigir

from operacionesCRUD import (
    obtener_todas_categorias,
    crear_categoria,
    obtener_categoria_por_id,
    editar_categoria,
    eliminar_categoria
)

# Ruta real: /admin/categorias
@admin_bp.route("/categorias")
def admin_mostrar_categorias():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    try:
        lista_categorias = obtener_todas_categorias()
    except Exception as e:
        flash(f"Error al cargar categorías: {e}", "error")
        lista_categorias = []
    
    return render_template(
        "admin_categorias.html", 
        categorias=lista_categorias,
        active_page="categorias" 
    )

# Ruta real: /admin/categoria/crear 
@admin_bp.route("/categoria/crear", methods=["POST"])
def admin_crear_categoria():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        # Esta ruta solo debe recibir POST
        return redirect(url_for('admin_bp.admin_mostrar_categorias'))

    nombre_cat = request.form.get('nombre_categoria')
    
    if not nombre_cat:
        flash("No puedes crear una categoría sin nombre.", "error")
        return redirect(url_for('admin_bp.admin_mostrar_categorias'))

    resultado = crear_categoria(nombre_cat)
    
    if isinstance(resultado, str): #error si devuelve texto
        flash(resultado, "error")
    else:
        flash("Categoría nueva creada.", "success")
    
    return redirect(url_for('admin_bp.admin_mostrar_categorias'))


# Ruta real: /admin/categoria/editar/ID...
@admin_bp.route("/categoria/editar/<cat_id_str>", methods=["GET", "POST"])
def admin_editar_categoria_ruta(cat_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    if request.method == "POST":
        nuevo_nombre = request.form.get('nombre')
        
        if not nuevo_nombre:
            flash("El nombre no puede estar vacío.", "error")
            return redirect(url_for('admin_bp.admin_editar_categoria_ruta', cat_id_str=cat_id_str))

        if editar_categoria(cat_id_str, nuevo_nombre):
            flash("Categoría actualizada con éxito.", "success")
        else:
            flash("No se pudo actualizar la categoría", "error")
        
        return redirect(url_for('admin_bp.admin_mostrar_categorias'))

    # Si es GET
    categoria = obtener_categoria_por_id(cat_id_str)
    if not categoria:
        flash("No se encontró esa categoría.", "error")
        return redirect(url_for('admin_bp.admin_mostrar_categorias'))

    return render_template(
        "admin_editar_categoria.html",
        categoria=categoria,
        active_page="categorias"
    )

# Ruta real: /admin/categoria/eliminar/ID...
@admin_bp.route("/categoria/eliminar/<cat_id_str>", methods=["POST"])
def admin_eliminar_categoria_ruta(cat_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()
        
    if eliminar_categoria(cat_id_str):
        flash("Categoría eliminada. También se quitó de todos los artículos.", "success")
    else:
        flash("No se pudo eliminar la categoría.", "error")
    
    return redirect(url_for('admin_bp.admin_mostrar_categorias'))