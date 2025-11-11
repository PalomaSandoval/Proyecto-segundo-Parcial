from flask import render_template, request, redirect, url_for, flash, session
from . import admin_bp, limpiar_sesion_y_redirigir
from operacionesCRUD import (
    obtener_todos_comentarios,
    eliminar_comentario_individual,
    Articulos_blog,
    agregar_comentario,
    obtener_comentario_por_id, 
    editar_comentario
    )


@admin_bp.route("/comentarios")
def admin_mostrar_comentarios():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    try:
        lista_comentarios = obtener_todos_comentarios()
        
        lista_articulos = Articulos_blog() 
    except Exception as e:
        flash(f"Error al cargar datos: {e}", "error")
        lista_comentarios = []
        lista_articulos = [] 

    return render_template(
        "admin_comentarios.html", 
        comentarios=lista_comentarios,
        articulos=lista_articulos, 
        active_page="comentarios" 
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


# Ruta real: /admin/comentario/crear
@admin_bp.route("/comentario/crear", methods=["POST"])
def admin_crear_comentario_ruta():
    
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    #Función CRUD
    texto_comentario = request.form.get('texto_comentario')
    id_del_articulo = request.form.get('articulo_id')
    id_del_admin = session['user_id'] 

    if not texto_comentario or not id_del_articulo:
        flash("Falta texto", "error")
        return redirect(url_for('admin_bp.admin_mostrar_comentarios'))

    
    resultado = agregar_comentario(id_del_articulo, id_del_admin, texto_comentario)

    if resultado:
        flash("Chisme agregado.", "success")
    else:
        flash("No se pudo pudo agregar el comentario", "error")

    return redirect(url_for('admin_bp.admin_mostrar_comentarios'))


# Ruta real: /admin/comentario/editar/ID...
@admin_bp.route("/comentario/editar/<comment_id_str>", methods=["GET", "POST"])
def admin_editar_comentario_ruta(comment_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()

    # "Guardar Cambios" (POST)
    if request.method == "POST":
        nuevo_texto = request.form.get('texto_comentario')

        if not nuevo_texto:
            flash("El comentario no puede ir vacío.", "error")
            return redirect(url_for('admin_bp.admin_editar_comentario_ruta', comment_id_str=comment_id_str))

        #función nueva del CRUD
        if editar_comentario(comment_id_str, nuevo_texto):
            flash("Comentario actualizado con éxito.", "success")
        else:
            flash("No se pudo actualizar el comentario.", "error")

        
        return redirect(url_for('admin_bp.admin_mostrar_comentarios'))

    comentario = obtener_comentario_por_id(comment_id_str)
    if not comentario:
        flash("No se encontró ese comentario.", "error")
        return redirect(url_for('admin_bp.admin_mostrar_comentarios'))

    return render_template(
        "admin_editar_comentario.html",
        comentario=comentario,
        active_page="comentarios" 
    )