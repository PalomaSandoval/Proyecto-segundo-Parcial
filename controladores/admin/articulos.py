from flask import render_template, request, redirect, url_for, flash, session
from . import admin_bp, limpiar_sesion_y_redirigir
# funciones de la BD que SÓLO este archivo usa
from operacionesCRUD import (
    Articulos_blog, 
    obtener_todas_categorias,  
    obtener_todos_tags,        
    crear_articulo,            
    eliminar_articulo,
    obtener_articulo_por_id,
    editar_articulo
)

# Ruta real: /admin/articulos
@admin_bp.route("/articulos")
def admin_mostrar_articulos():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    try:
        lista_articulos = Articulos_blog()
    except Exception as e:
        flash(f"Error al cargar artículos: {e}")
        lista_articulos = []
    
    return render_template(
        "admin_articulos.html", 
        articulos=lista_articulos,
        active_page="articulos"
    )

# Ruta real: /admin/articulo/eliminar/ID...
@admin_bp.route("/articulo/eliminar/<article_id_str>", methods=["POST"])
def admin_eliminar_articulo(article_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()
        
    if eliminar_articulo(article_id_str):
        flash("Artículo y sus comentarios eliminados con éxito.", "success")
    else:
        flash("No se pudo eliminar el artículo.", "error")
    
    return redirect(url_for('admin_bp.admin_mostrar_articulos'))


# Ruta real: /admin/articulo/editar/ID...
@admin_bp.route("/articulo/editar/<article_id_str>", methods=["GET", "POST"])
def admin_editar_articulo_ruta(article_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    if request.method == "POST":
        titulo = request.form.get('titulo')
        texto = request.form.get('texto')
        ids_categorias = request.form.getlist('categorias')
        ids_tags = request.form.getlist('tags')

        if not ids_categorias or not ids_tags:
            flash("Debes elegir al menos una categoría Y un tag.", "error")
            articulo = obtener_articulo_por_id(article_id_str)
            todas_las_categorias = obtener_todas_categorias()
            todos_los_tags = obtener_todos_tags()
            articulo['title'] = titulo 
            articulo['text'] = texto
            articulo['categories'] = ids_categorias 
            articulo['tags'] = ids_tags

            return render_template(
                "admin_editar_articulo.html",
                articulo=articulo,
                all_categories=todas_las_categorias,
                all_tags=todos_los_tags,
                active_page="articulos"
            )
        
        exito = editar_articulo(article_id_str, titulo, texto, ids_categorias, ids_tags)

        if exito:
            flash("Artículo actualizado con éxito.", "success")
        else:
            flash("No se pudo actualizar el artículo.", "error")
        
        return redirect(url_for('admin_bp.admin_mostrar_articulos'))

    # Si es GET
    articulo = obtener_articulo_por_id(article_id_str)
    if not articulo:
        flash("No se encontró ese artículo.", "error")
        return redirect(url_for('admin_bp.admin_mostrar_articulos'))

    try:
        todas_las_categorias = obtener_todas_categorias()
        todos_los_tags = obtener_todos_tags()
    except Exception as e:
        flash(f"Error al cargar categorías/tags: {e}", "error")
        todas_las_categorias = []
        todos_los_tags = []

    return render_template(
        "admin_editar_articulo.html",
        articulo=articulo,
        all_categories=todas_las_categorias,
        all_tags=todos_los_tags,
        active_page="articulos"
    )

# Ruta real: /admin/articulo/crear
@admin_bp.route("/articulo/crear", methods=["GET", "POST"])
def admin_crear_articulo_ruta():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    if request.method == "POST":
        titulo = request.form.get('titulo')
        texto = request.form.get('texto')
        ids_categorias = request.form.getlist('categorias')
        ids_tags = request.form.getlist('tags')

        if not titulo or not texto or not ids_categorias or not ids_tags:
            flash("Todos los campos son obligatorios (título, texto, categoria y tag).", "error")
            
            todas_las_categorias = obtener_todas_categorias()
            todos_los_tags = obtener_todos_tags()
            articulo_borrador = {
                "title": titulo,
                "text": texto,
                "categories": ids_categorias,
                "tags": ids_tags
            }

            return render_template(
                "admin_crear_articulo.html",
                articulo=articulo_borrador,
                all_categories=todas_las_categorias,
                all_tags=todos_los_tags,
                active_page="articulos"
            )
        
        user_id_del_admin = session['user_id']
        inserted_id = crear_articulo(user_id_del_admin, titulo, texto, ids_categorias, ids_tags)

        if inserted_id:
            flash("Artículo nuevo publicado.", "success")
            return redirect(url_for('admin_bp.admin_mostrar_articulos'))
        else:
            flash("No se pudo crear el artículo.", "error")
            return redirect(url_for('admin_bp.admin_crear_articulo_ruta'))

    # Si es GET
    try:
        todas_las_categorias = obtener_todas_categorias()
        todos_los_tags = obtener_todos_tags()
    except Exception as e:
        flash(f"Error al cargar categorías/tags: {e}", "error")
        todas_las_categorias = []
        todos_los_tags = []

    return render_template(
        "admin_crear_articulo.html",
        articulo={}, 
        all_categories=todas_las_categorias,
        all_tags=todos_los_tags,
        active_page="articulos" 
    )