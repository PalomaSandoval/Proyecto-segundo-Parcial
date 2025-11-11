from flask import (
    Blueprint, redirect, url_for, flash, session
)
#se crea para extraer los html 
admin_bp = Blueprint(
    'admin_bp', __name__,
    template_folder='templates',
    url_prefix='/admin' 
)

# limpiar_sesion_y_redirigir
def limpiar_sesion_y_redirigir():
    flash(" ", "error")
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    return redirect(url_for('auth_bp.index'))


from . import dashboard
from . import usuarios
from . import articulos
from . import categorias
from . import tags
from . import comentarios 