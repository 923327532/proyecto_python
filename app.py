from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import get_db_connection
from colas import cola
import random
import admin  
import usuario 
import correo
import yape 
from correo import enviar_correo
from psycopg2.extras import RealDictCursor 
app = Flask(__name__)
app.secret_key = "lopez"

app.register_blueprint(admin.admin_bp)
app.register_blueprint(usuario.user_bp)
app.register_blueprint(yape.yape_bp)

def validar_usuario(user, password):
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)  
    cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (user,))
    usuario = cursor.fetchone()
    cursor.close()
    db.close()
    if usuario and check_password_hash(usuario['password'], password):
        return usuario
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['usuario']
        password = request.form['clave']
        usuario_db = validar_usuario(user, password)
        if usuario_db:
            session['usuario'] = {
                'id': usuario_db['id'],
                'usuario': usuario_db['usuario'],
                'perfil': usuario_db['perfil']
            }

            # Enviar correo de inicio de sesión
            mensaje = f"""
            <h3>Inicio de sesión en Banco TECSUP</h3>
            <p>Hola <strong>{usuario_db['usuario']}</strong>, acabas de iniciar sesión correctamente.</p>
            <p>Si no fuiste tú, por favor contacta al soporte.</p>
            """
            enviar_correo(usuario_db['correo'], "Inicio de sesión detectado", mensaje)

            if usuario_db['perfil'] == 'cliente':
                if not cola.existe(usuario_db['usuario']):
                    if cola.encolar(usuario_db['usuario']):
                        return redirect(url_for('user.usuario_home'))
                    else:
                        flash('La cola está llena, intenta más tarde', 'warning')
                        return redirect(url_for('login'))
                else:
                    return redirect(url_for('user.usuario_home'))
            elif usuario_db['perfil'] == 'admin':
                return redirect(url_for('admin.admin_home'))
        else:
            flash('Usuario o clave incorrectos', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

def generar_numero_cuenta():
    return "CU" + str(random.randint(10000000000000, 99999999999999))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario_form = request.form['usuario']
        password = request.form['password']
        correo_form = request.form['correo']
        rol = 'cliente'  

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario_form,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            flash('El usuario ya existe', 'danger')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        numero_cuenta = generar_numero_cuenta()

        cursor.execute("INSERT INTO usuarios (usuario, password, perfil, numero_cuenta, correo) VALUES (%s, %s, %s, %s, %s)",
                       (usuario_form, password_hash, rol, numero_cuenta, correo_form))
        db.commit()

        cursor.close()
        db.close()

        mensaje = f"""
        <h3>¡Bienvenido a Banco TECSUP!</h3>
        <p>Tu cuenta ha sido creada exitosamente con el correo <strong>{correo_form}</strong>.</p>
        <p>Puedes iniciar sesión cuando quieras. ¡Gracias por confiar en nosotros!</p>
        """
        enviar_correo(correo_form, "Cuenta creada en Banco TECSUP", mensaje)

        flash('Registro exitoso. Inicia sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
