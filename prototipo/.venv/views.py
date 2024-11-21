from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from db import mysql

views = Blueprint("views", __name__)

# URLs de los microservicios
validation_url = "http://127.0.0.1:8000/validate_score/"
calculation_url = "http://127.0.0.1:8001/calculate_score/"

# Página de inicio
@views.route("/")
def home():
    return render_template("home.html")

# Inicio de sesión de jueces
@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user is None:
            flash("Usuario no encontrado. Credenciales incorrectas.")
            return redirect(url_for("views.login"))

        # Para comparación directa de contraseñas en texto plano (solo para pruebas)
        if password == user[1]:
            session['logged_in'] = True
            session['user_id'] = user[0]
            flash("Inicio de sesión exitoso.")
            return redirect(url_for("views.dashboard"))
        else:
            flash("Contraseña incorrecta.")
            return redirect(url_for("views.login"))

    return render_template("login.html")

# Panel de administración para jueces
@views.route("/dashboard")
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for("views.login"))
    return render_template("dashboard.html")

# Cerrar sesión
@views.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("views.home"))

# Ruta para agregar un nuevo participante
@views.route("/add_participant", methods=["GET", "POST"])
def add_participant():
    if not session.get('logged_in'):
        return redirect(url_for("views.login"))
    
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        country = request.form["country"]
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO participants (name, age, country, current_score) VALUES (%s, %s, %s, 0)", (name, age, country))
        mysql.connection.commit()
        cursor.close()
        
        flash("Participante agregado con éxito.")
        return redirect(url_for("views.dashboard"))
    return render_template("add_participant.html")

# Ruta para registrar el puntaje de un participante
@views.route("/score", methods=["GET", "POST"])
def score():
    if not session.get('logged_in'):
        return redirect(url_for("views.login"))
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name FROM participants")
    participants = cursor.fetchall()
    
    error_message = None  # Variable para almacenar el mensaje de error

    if request.method == "POST":
        participant_id = request.form["participant_id"]
        difficulty = float(request.form["difficulty"])
        execution = float(request.form["execution"])
        penalties = float(request.form["penalties"])

        # Función para validar un puntaje usando el microservicio de validación
        def validate_score(score_data):
            response = requests.post(validation_url, json=score_data)
            return response.json()

        # Validar los valores de dificultad, ejecución y penalizaciones
        score_data = {
            "difficulty": difficulty,
            "execution": execution,
            "penalties": penalties
        }
        validation_response = validate_score(score_data)

        if validation_response["valid"]:
            # Llamar al microservicio de cálculo para obtener el puntaje total
            calculation_response = requests.post(calculation_url, json=score_data)
            total_score = calculation_response.json().get("total_score")

            # Guardar puntaje en la tabla scores
            cursor.execute("""
                INSERT INTO scores (participant_id, difficulty, execution, penalties, total_score) 
                VALUES (%s, %s, %s, %s, %s)
            """, (participant_id, difficulty, execution, penalties, total_score))
            
            # Actualizar el puntaje actual del participante en la tabla participants
            cursor.execute("UPDATE participants SET current_score = %s WHERE id = %s", (total_score, participant_id))
            mysql.connection.commit()
            
            flash("Puntaje registrado con éxito. Confirmamos que los resultados están dentro del rango.")
            return redirect(url_for("views.dashboard"))
        else:
            # Captura el mensaje de error específico del microservicio
            error_message = validation_response["message"]
    
    cursor.close()
    return render_template("score.html", participants=participants, error_message=error_message)

# Ruta para listar los participantes
@views.route("/participants")
def participants_list():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name, age, country, current_score FROM participants")
    participants = cursor.fetchall()
    cursor.close()
    return render_template("participants_list.html", participants=participants)

# Ruta para mostrar los resultados
@views.route("/results")
def results():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT p.name, s.total_score, s.difficulty, s.execution, s.penalties FROM scores s JOIN participants p ON s.participant_id = p.id")
    results = cursor.fetchall()
    cursor.close()
    return render_template("results.html", results=results)

@views.route("/test_db")
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        cursor.close()
        return f"Conexión exitosa. Tablas en la base de datos: {tables}"
    except Exception as e:
        return f"Error al conectar a la base de datos: {e}"
