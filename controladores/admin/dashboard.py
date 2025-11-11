# --- Guardar como: controladores/admin/dashboard.py ---

from flask import render_template, session
from . import admin_bp, limpiar_sesion_y_redirigir

# La ruta será /admin/dashboard
@admin_bp.route("/dashboard")
def admin_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()
    
    return render_template("admin_dashboard.html", active_page="dashboard")