from flask import Flask

# blueprints 
from controladores.auth_routes import auth_bp

from controladores.admin import admin_bp 

#Se crea la app
app = Flask(__name__)
app.config['SECRET_KEY'] = '0'

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)


if __name__ == "__main__":
    app.run(debug=True)