# pago_stripe/app.py
import os
import ollama
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import stripe


# Login
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)


# Base de datos
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------
load_dotenv()


stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


app = Flask(
    __name__,
    static_folder="../donostigo",
    template_folder="templates"
)


app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


# Configuración de la base de datos
# Fíjate que después de 'root:' NO hay nada antes del '@'
# Usamos 127.0.0.1 que es la dirección física de tu ordenador
# Cambia esto en tu app.py
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://donostigo:donostigo@174.129.28.83:3306/donostigo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Inicialización de SQLAlchemy
db = SQLAlchemy(app)


# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"


# --------------------------------------------------
# MODELO DE USUARIO
# --------------------------------------------------
# --------------------------------------------------
# MODELOS DE DATOS
# --------------------------------------------------
# --------------------------------------------------
# MODELO DE USUARIO
# --------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    # AÑADE ESTA LÍNEA AQUÍ:
    username = db.Column(db.String(50), unique=True, nullable=False) 
    
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
   
    # Datos del viaje
    origen = db.Column(db.String(255), nullable=False)
    destino = db.Column(db.String(255), nullable=False)
    fecha_viaje = db.Column(db.String(100), nullable=False)
    tipo_servicio = db.Column(db.String(50), nullable=False)
   
    # Datos adicionales
    num_vuelo = db.Column(db.String(20), nullable=True)
    pasajeros = db.Column(db.Integer, default=1)
    monto_total = db.Column(db.Float, nullable=False)


    def __repr__(self):
        return f'<Reserva {self.id} - {self.tipo_servicio}>'
# Tabla auxiliar para la relación muchos-a-muchos de favoritos
favoritos = db.Table('favoritos',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('servicio_id', db.String(50), primary_key=True) # Usamos el ID que pusiste en el HTML
)


class Valoracion(db.Model):
    __tablename__ = 'valoraciones'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    servicio_id = db.Column(db.String(50), nullable=False)
    puntuacion = db.Column(db.Integer, nullable=False) # 1 a 5
    comentario = db.Column(db.Text, nullable=True)


# Actualiza la clase User para que conozca sus favoritos
# Añade esta línea DENTRO de la clase User:
# favoritos = db.relationship('User', secondary=favoritos, backref='usuarios_que_aman')
# --------------------------------------------------
# CARGADOR DE USUARIO (Versión moderna 2.0)
# --------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    # Cambiamos .query.get() por db.session.get() para evitar avisos de deprecación
    return db.session.get(User, int(user_id))
# --------------------------------------------------
# RUTAS PÁGINAS
# --------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("registro.html")  # Tu HTML con React


@app.route("/reserva")
@login_required
def reserva():
    return render_template("aeropuerto.html")


# --------------------------------------------------
# API AUTENTICACIÓN PARA REACT
# --------------------------------------------------
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Datos incompletos"}), 400



    if User.query.filter_by(email=email).first():
        return jsonify({"error": "El usuario ya existe"}), 409


    hashed_password = generate_password_hash(password)


    user = User(email=email, username=email, password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()


    login_user(user)
    return jsonify({"message": "Registro correcto"})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()


    email = data.get("email")
    password = data.get("password")


    user = User.query.filter_by(email=email).first()


    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Credenciales incorrectas"}), 401


    login_user(user)
    return jsonify({"message": "Login correcto"})


@app.route("/api/logout", methods=["POST"])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Sesión cerrada"})


# --------------------------------------------------
# STRIPE (PROTEGIDO)
# --------------------------------------------------
@app.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    data = request.get_json()


    destination = data.get("destination")
    amount = data.get("amount")  # en céntimos


    if not destination or not amount:
        return jsonify({"error": "Faltan datos"}), 400


    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "unit_amount": amount,
                "product_data": {
                    "name": f"Taxi a {destination}"
                },
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://localhost:5000/success",
        cancel_url="http://localhost:5000/cancel"
    )


    return jsonify({"url": session.url})


# --------------------------------------------------
# PÁGINAS DE RESULTADOS DE PAGO
# --------------------------------------------------
@app.route("/success")
@login_required
def success():
    return """
    <h1>Pago realizado con éxito</h1>
    <p>La operación se ha completado correctamente.</p>
    """




@app.route("/cancel")
@login_required
def cancel():
    return "<h1>Pago cancelado ❌</h1>"


# --------------------------------------------------
# DEBUG / INFO
# --------------------------------------------------
@app.route("/whoami")
@login_required
def whoami():
    return jsonify({
        "id": current_user.id,
        "email": current_user.email
    })





# --------------------------------------------------
# API FAVORITOS Y VALORACIONES
# --------------------------------------------------


@app.route("/api/favoritos/<servicio_id>", methods=["POST"])
@login_required
def toggle_favorito(servicio_id):
    try:
        # 1. Buscamos si ya existe el registro usando SQL directo (más seguro para tablas manuales)
        check_sql = db.text("SELECT * FROM favoritos WHERE usuario_id = :u_id AND servicio_id = :s_id")
        existe = db.session.execute(check_sql, {"u_id": current_user.id, "s_id": servicio_id}).fetchone()


        if existe:
            # 2. Si existe, lo borramos
            delete_sql = db.text("DELETE FROM favoritos WHERE usuario_id = :u_id AND servicio_id = :s_id")
            db.session.execute(delete_sql, {"u_id": current_user.id, "s_id": servicio_id})
            mensaje = "Eliminado de favoritos"
        else:
            # 3. Si no existe, lo añadimos
            insert_sql = db.text("INSERT INTO favoritos (usuario_id, servicio_id) VALUES (:u_id, :s_id)")
            db.session.execute(insert_sql, {"u_id": current_user.id, "s_id": servicio_id})
            mensaje = "Añadido a favoritos ❤️"


        db.session.commit()
        return jsonify({"message": mensaje}), 200


    except Exception as e:
        db.session.rollback()
        print(f"Error en favoritos: {e}")
        return jsonify({"error": "Error al procesar el favorito"}), 500


@app.route("/api/valoraciones", methods=["POST"])
@login_required
def api_valoracion():
    data = request.get_json()
    nueva_val = Valoracion(
        user_id=current_user.id,
        servicio_id=data.get("service_id"),
        puntuacion=data.get("rating"),
        comentario=data.get("comment")
    )
    db.session.add(nueva_val)
    db.session.commit()
    return jsonify({"message": "Valoración guardada correctamente"})


@app.route("/api/ia", methods=["POST"])
def chat_ia():
    data = request.get_json()
    mensaje_usuario = data.get('message')

    try:
        # Llamada a Ollama (usaremos llama3 por defecto)
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': mensaje_usuario,
            },
        ])
        
        respuesta_ia = response['message']['content']
        return jsonify({"reply": respuesta_ia})

    except Exception as e:
        print(f"Error con Ollama: {e}")
        return jsonify({"reply": "Lo siento, mi sistema de IA está reiniciando."}), 500


# --------------------------------------------------
# INIT DB Y EJECUCIÓN
# --------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    # host="0.0.0.0" permite que el servidor de Nazaret sea accesible
    app.run(host="0.0.0.0", port=5000, debug=True)


