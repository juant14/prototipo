from flask import Flask
from db import mysql
from views import views

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'my-secret-pw'
app.config['MYSQL_DB'] = 'gym_app'

# Inicialización de MySQL
mysql.init_app(app)

# Registrar el blueprint
app.register_blueprint(views, url_prefix="/views")

if __name__ == '__main__':
    app.run(debug=True)
