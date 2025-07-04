from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from config import get_db_connection
from datetime import datetime, timedelta
from colas import cola
from flask import jsonify
import psycopg2.extras

user_bp = Blueprint('user', __name__, url_prefix='/usuario')

def validar_cliente():
    return 'usuario' in session and session['usuario']['perfil'] == 'cliente'

@user_bp.route('/')
def usuario_home():
    if not validar_cliente():
        return redirect(url_for('login'))
    db = get_db_connection()
    cursor = db.cursor()
    usuario = session['usuario']['usuario']

    # Traer saldo y deuda para calificación
    cursor.execute("SELECT saldo FROM usuarios WHERE usuario = %s", (usuario,))
    saldo = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(monto) FROM prestamos WHERE usuario = %s AND estado = 'Pendiente'", (usuario,))
    deuda = cursor.fetchone()[0] or 0

    calificacion = calcular_calificacion(saldo, deuda)

    # Otros datos para mostrar
    cursor.execute("SELECT destinatario, monto, fecha FROM transferencias WHERE remitente = %s ORDER BY fecha DESC", (usuario,))
    historial = cursor.fetchall()

    cursor.execute("SELECT descripcion, monto, fecha FROM pagos WHERE usuario = %s ORDER BY fecha DESC", (usuario,))
    pagos = cursor.fetchall()

    cursor.execute("SELECT id, sueldo, tarjeta_solicitada, estado FROM solicitudes_tarjetas WHERE usuario = %s ORDER BY id DESC", (usuario,))
    mis_solicitudes = cursor.fetchall()

    cursor.execute("SELECT monto, meses, cuota, interes, estado, fecha FROM prestamos WHERE usuario = %s ORDER BY fecha DESC", (usuario,))
    prestamos = cursor.fetchall()

    cursor.execute("SELECT mensaje, respuesta, fecha FROM mensajes WHERE usuario = %s ORDER BY fecha DESC", (usuario,))
    mensajes = cursor.fetchall()

    cursor.execute("SELECT remitente, monto, fecha FROM transferencias WHERE destinatario = %s ORDER BY fecha DESC", (usuario,))
    recibidas = cursor.fetchall()



    cinco_dias_atras = datetime.now() - timedelta(days=5)
    cursor.execute("""
        SELECT 'Transferencia' AS tipo, destinatario AS detalle, monto, fecha
        FROM transferencias
        WHERE remitente = %s AND fecha >= %s
        UNION
        SELECT 'Pago' AS tipo, descripcion AS detalle, monto, fecha
        FROM pagos
        WHERE usuario = %s AND fecha >= %s
        ORDER BY fecha DESC
    """, (usuario, cinco_dias_atras, usuario, cinco_dias_atras))
    cambios = cursor.fetchall()

    cursor.execute("SELECT numero_cuenta FROM usuarios WHERE usuario = %s", (usuario,))
    nc_row = cursor.fetchone()
    numero_cuenta = nc_row[0] if nc_row else "0000000000000000"
    cursor.close()
    db.close()

    return render_template('usuario/usuario.html', 
                           nombre=usuario,
                           historial=historial,
                           pagos=pagos,
                           mis_solicitudes=mis_solicitudes,
                           prestamos=prestamos,
                           mensajes=mensajes,
                           saldo=saldo,
                           calificacion=calificacion,
                           cambios=cambios,
                           numero_cuenta=numero_cuenta,
                           recibidas=recibidas
                          )

@user_bp.route('/transferencia', methods=['GET', 'POST'])
def transferencia():
    if not validar_cliente():
        return redirect(url_for('login'))

    remitente = session['usuario']['usuario']
    db = get_db_connection()
    cursor = db.cursor()

    usuario_destinatario = None  
    error = None

    if request.method == 'POST':
        cuenta_destino = request.form.get('cuenta_destino', '').strip()
        monto_str = request.form.get('monto', '').strip()
        confirmar = request.form.get('confirmar', '') 

        # Buscar usuario destinatario para mostrar el nombre
        cursor.execute("SELECT usuario FROM usuarios WHERE numero_cuenta = %s", (cuenta_destino,))
        resultado = cursor.fetchone()
        if resultado:
            usuario_destinatario = resultado[0]
        else:
            flash("La cuenta destino no existe", "error")
            usuario_destinatario = None

        # Si no existe usuario destino o no está confirmada la transferencia, solo mostramos el nombre para confirmar
        if not usuario_destinatario or confirmar != 'si':
            historial = obtener_historial(cursor, remitente)
            cursor.close()
            db.close()
            return render_template('usuario/realizar_trasferencia.html', 
                                   historial=historial,
                                   usuario_destinatario=usuario_destinatario,
                                   cuenta_destino=cuenta_destino,
                                   monto=monto_str)

        # Si llegó aquí es porque se confirmó la transferencia, seguimos validando y haciendo transferencia
        try:
            monto = float(monto_str)
            if monto <= 0:
                flash("Monto debe ser positivo", "error")
                raise ValueError("Monto no positivo")
        except ValueError:
            flash("Monto inválido", "error")
            historial = obtener_historial(cursor, remitente)
            cursor.close()
            db.close()
            return render_template('usuario/realizar_trasferencia.html',
                                   historial=historial,
                                   usuario_destinatario=usuario_destinatario,
                                   cuenta_destino=cuenta_destino,
                                   monto=monto_str)

        cursor.execute("SELECT saldo FROM usuarios WHERE usuario = %s", (remitente,))
        saldo_remitente = cursor.fetchone()
        if not saldo_remitente:
            flash("No se encontró el usuario remitente", "error")
            historial = obtener_historial(cursor, remitente)
            cursor.close()
            db.close()
            return render_template('usuario/realizar_trasferencia.html',
                                   historial=historial,
                                   usuario_destinatario=usuario_destinatario,
                                   cuenta_destino=cuenta_destino,
                                   monto=monto_str)

        if saldo_remitente[0] < monto:
            flash("Saldo insuficiente", "error")
            historial = obtener_historial(cursor, remitente)
            cursor.close()
            db.close()
            return render_template('usuario/realizar_trasferencia.html',
                                   historial=historial,
                                   usuario_destinatario=usuario_destinatario,
                                   cuenta_destino=cuenta_destino,
                                   monto=monto_str)

        try:
            cursor.execute("UPDATE usuarios SET saldo = saldo - %s WHERE usuario = %s", (float(monto), remitente))
            cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE usuario = %s", (float(monto), usuario_destinatario))
            cursor.execute(
                "INSERT INTO transferencias (remitente, destinatario, monto, fecha) VALUES (%s, %s, %s, NOW())",
                (remitente, usuario_destinatario,float( monto))
            )
            db.commit()
            flash(f"Transferencia realizada con éxito a {usuario_destinatario}", "success")
        except Exception as e:
            db.rollback()
            flash(f"Error al realizar transferencia: {e}", "error")

    # Mostrar historial actualizado en GET y POST
    historial = obtener_historial(cursor, remitente)

    cursor.close()
    db.close()
    return render_template('usuario/realizar_trasferencia.html', 
                           historial=historial,
                           usuario_destinatario=usuario_destinatario)


def obtener_historial(cursor, remitente):
    cursor.execute(
        "SELECT destinatario, monto, fecha FROM transferencias WHERE remitente = %s ORDER BY fecha DESC",
        (remitente,)
    )
    return cursor.fetchall()




@user_bp.route('/verificar_cuenta/<cuenta>')
def verificar_cuenta(cuenta):
    cuenta = cuenta.strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario FROM usuarios WHERE numero_cuenta = %s", (cuenta,))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    if resultado:
        return jsonify({'encontrado': True, 'usuario': resultado[0]})
    else:
        return jsonify({'encontrado': False})



@user_bp.route('/prestamo', methods=['GET', 'POST'])
def prestamo():
    if not validar_cliente():
        return redirect(url_for('login'))

    usuario = session['usuario']['usuario']

    if request.method == 'POST':
        try:
            monto = float(request.form['monto'])
            meses = int(request.form['meses'])

            if monto <= 0 or meses <= 0:
                flash("Monto y meses deben ser mayores a cero", "error")
                return redirect(url_for('user.prestamo'))

            interes = 5.0
            cuota = (monto * (1 + interes / 100)) / meses
            fecha = datetime.now().strftime('%Y-%m-%d')

            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""INSERT INTO prestamos (usuario, monto, meses, interes, cuota, estado, fecha)
                              VALUES (%s, %s, %s, %s, %s, 'Pendiente', %s)""",
                           (usuario, monto, meses, interes, cuota, fecha))
            db.commit()
            flash("Solicitud de préstamo enviada", "success")

        except Exception as e:
            db.rollback()
            flash(f"Error al enviar solicitud: {e}", "error")

        finally:
            cursor.close()
            db.close()

        return redirect(url_for('user.prestamo'))

    # GET: mostrar formulario y préstamos
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""SELECT monto, meses, cuota, interes, estado, fecha 
                      FROM prestamos WHERE usuario = %s ORDER BY fecha DESC""", (usuario,))
    prestamos = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('usuario/solicitar_prestamos.html', prestamos=prestamos)




@user_bp.route('/pago', methods=['GET', 'POST'])
def pago():
    if not validar_cliente():
        return redirect(url_for('login'))

    usuario = session['usuario']['usuario']

    if request.method == 'POST':
        descripcion = request.form['descripcion'].strip()
        monto_str = request.form['monto']

        if not descripcion:
            flash("Descripción del pago es requerida", "error")
            return redirect(url_for('user.pago'))

        try:
            monto = float(monto_str)
            if monto <= 0:
                flash("Monto inválido para pago", "error")
                return redirect(url_for('user.pago'))
        except ValueError:
            flash("Monto inválido para pago", "error")
            return redirect(url_for('user.pago'))

        db = get_db_connection()
        cursor = db.cursor()
        try:
            # ✅ Obtener saldo actual
            cursor.execute("SELECT saldo FROM usuarios WHERE usuario = %s", (usuario,))
            resultado = cursor.fetchone()
            if not resultado:
                flash("No se encontró el usuario", "error")
                return redirect(url_for('user.pago'))

            saldo_actual = resultado[0]
            if saldo_actual < monto:
                flash("Saldo insuficiente para realizar el pago", "error")
                return redirect(url_for('user.pago'))

            # ✅ Registrar pago y descontar saldo
            cursor.execute(
                "INSERT INTO pagos (usuario, descripcion, monto, fecha) VALUES (%s, %s, %s, NOW())",
                (usuario, descripcion, monto)
            )
            cursor.execute(
                "UPDATE usuarios SET saldo = saldo - %s WHERE usuario = %s",
                (monto, usuario)
            )
            db.commit()
            flash("Pago registrado y saldo descontado correctamente", "success")

        except Exception as e:
            db.rollback()
            flash(f"Error al registrar pago: {e}", "error")
        finally:
            cursor.close()
            db.close()

        return redirect(url_for('user.pago'))

    # GET: mostrar formulario + historial de 30 días
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    hace_30_dias = datetime.now() - timedelta(days=30)
    cursor.execute(
        "SELECT descripcion, monto, fecha FROM pagos WHERE usuario = %s AND fecha >= %s ORDER BY fecha DESC",
        (usuario, hace_30_dias)
    )
    pagos_recientes = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('usuario/realizar_pago.html', pagos=pagos_recientes)




@user_bp.route('/mensaje', methods=['POST'])
def mensaje():
    if not validar_cliente():
        return redirect(url_for('login'))

    usuario = session['usuario']['usuario']
    contenido = request.form['mensaje'].strip()
    if not contenido:
        flash("Mensaje no puede estar vacío", "error")
        return redirect(url_for('user.usuario_home'))

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO mensajes (usuario, mensaje) VALUES (%s, %s)", (usuario, contenido))
    db.commit()
    cursor.close()
    db.close()
    flash("Mensaje enviado", "success")
    return redirect(url_for('user.usuario_home'))


@user_bp.route('/entrar_cola')
def entrar_cola():
    if not validar_cliente():
        return redirect(url_for('login'))

    cola.encolar(session['usuario'])
    return f"Estás en la cola. Usuarios en espera: {cola.mostrar()}"


@user_bp.route('/solicitar_tarjeta', methods=['GET', 'POST'])
def solicitar_tarjeta():
    if not validar_cliente():
        return redirect(url_for('login'))

    usuario = session['usuario']['usuario']
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            sueldo = float(request.form['sueldo'])
            tarjeta = request.form['tarjeta_solicitada']

            cursor.execute("""
                INSERT INTO solicitudes_tarjetas (usuario, sueldo, tarjeta_solicitada, estado)
                VALUES (%s, %s, %s, 'Pendiente')
            """, (usuario, sueldo, tarjeta))
            db.commit()
            flash("Solicitud registrada con éxito.", "success")
        except Exception as e:
            db.rollback()
            flash(f"Error al registrar la solicitud: {e}", "error")

    # Obtener las solicitudes del usuario
    cursor.execute("""
        SELECT id, usuario, sueldo, tarjeta_solicitada, estado, fecha_solicitud
        FROM solicitudes_tarjetas
        WHERE usuario = %s
        ORDER BY id DESC
    """, (usuario,))
    
    solicitudes = cursor.fetchall()
    cursor.close()
    db.close()

    # Convertir los resultados a objetos con nombre de atributo (opcional pero útil con tu HTML)
    mis_solicitudes = [
        {
            'id': row[0],
            'usuario': row[1],
            'sueldo': row[2],
            'tarjeta_solicitada': row[3],
            'estado': row[4],
            'fecha_solicitud': row[5],
        }
        for row in solicitudes
    ]

    return render_template('usuario/solicitar_tarjeta.html', mis_solicitudes=mis_solicitudes)

@user_bp.route('/cancelar_solicitud/<int:id>', methods=['POST'])
def cancelar_solicitud(id):
    if not validar_cliente():
        return redirect(url_for('login'))

    usuario = session['usuario']['usuario']
    db = get_db_connection()
    cursor = db.cursor()

    # Verificamos que sea del mismo usuario y que esté pendiente
    cursor.execute("""
        SELECT estado FROM solicitudes_tarjetas
        WHERE id = %s AND usuario = %s
    """, (id, usuario))
    solicitud = cursor.fetchone()

    if solicitud and solicitud[0] == "Pendiente":
        cursor.execute("""
            UPDATE solicitudes_tarjetas
            SET estado = 'Cancelada'
            WHERE id = %s
        """, (id,))
        db.commit()
        flash("Solicitud cancelada correctamente.", "success")
    else:
        flash("No se pudo cancelar la solicitud.", "error")

    cursor.close()
    db.close()
    return redirect(url_for('user.solicitar_tarjeta'))



def calcular_calificacion(sueldo, deuda):
    if deuda == 0:
        return "Excelente"
    ratio = deuda / sueldo if sueldo > 0 else 1
    if ratio < 0.3:
        return "Buena"
    elif ratio < 0.6:
        return "Regular"
    else:
        return "Mala"
    

@user_bp.route('/usuario/cambiar_moneda', methods=['GET', 'POST'])
def cambiar_moneda_usuario():
    db = get_db_connection()
    resultado = None
    saldo_dolares = 0.00

    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Obtener la tasa de cambio desde la tabla tipo_cambio
    cursor.execute("SELECT valor FROM tipo_cambio WHERE tipo = 'USD_PEN'")
    fila_cambio = cursor.fetchone()
    tasa_cambio = float(fila_cambio['valor']) if fila_cambio else float('3.8')

    # Obtener datos de sesión
    usuario_data = session.get('usuario')
    if isinstance(usuario_data, dict):
        nombre_usuario = usuario_data.get('usuario')
    else:
        nombre_usuario = usuario_data

    if not nombre_usuario:
        flash('Usuario no autenticado.')
        return redirect(url_for('login'))

    cursor.execute('SELECT id, saldo FROM usuarios WHERE usuario = %s', (nombre_usuario,))
    user = cursor.fetchone()

    if user is None:
        flash('Usuario no encontrado.')
        return render_template('usuario/cambiar_moneda.html', resultado=None, tasa=tasa_cambio)

    cursor.execute('SELECT saldo_dolares FROM cuenta_dolares WHERE usuario_id = %s', (user['id'],))
    cuenta = cursor.fetchone()
    if cuenta:
        saldo_dolares = float(cuenta['saldo_dolares'])

    if request.method == 'POST':
        monto_str = request.form.get('monto')
        try:
            monto = float(monto_str)
            saldo_actual = float(user['saldo'])

            if monto > saldo_actual:
                flash('Saldo insuficiente.')
                return render_template('usuario/cambiar_moneda.html', resultado=None, tasa=tasa_cambio, saldo_dolares=saldo_dolares)

            nuevo_saldo = saldo_actual - monto
            cursor.execute('UPDATE usuarios SET saldo = %s WHERE id = %s', (nuevo_saldo, user['id']))
            db.commit()

            monto_dolares = round(monto / float(tasa_cambio), 2)

            # Insertar o actualizar cuenta en dólares
            if cuenta:
                nuevo_saldo_dolares = float(cuenta['saldo_dolares']) + monto_dolares
                cursor.execute('UPDATE cuenta_dolares SET saldo_dolares = %s WHERE usuario_id = %s', (nuevo_saldo_dolares, user['id']))
            else:
                nuevo_saldo_dolares = monto_dolares
                cursor.execute('INSERT INTO cuenta_dolares (usuario_id, saldo_dolares) VALUES (%s, %s)', (user['id'], nuevo_saldo_dolares))
            db.commit()

            saldo_dolares = nuevo_saldo_dolares
            resultado = f"Cuenta en dólares actualizada: tienes ahora ${saldo_dolares:.2f} (S/ {monto} convertidos)."

        except ValueError:
            flash('Monto inválido.')

    return render_template(
        'usuario/cambiar_moneda.html',
        resultado=resultado,
        tasa=tasa_cambio,
        saldo_dolares=saldo_dolares,
        saldo_soles=user['saldo']
    )


@user_bp.route('/usuario/pagar_tarjeta', methods=['GET', 'POST'])
def pagar_tarjeta():
    db = get_db_connection()
    mensaje = None
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    usuario_data = session.get('usuario')
    if isinstance(usuario_data, dict):
        nombre_usuario = usuario_data.get('usuario')
    else:
        nombre_usuario = usuario_data

    if not nombre_usuario:
        flash('Usuario no autenticado.')
        return redirect(url_for('login'))

    cursor.execute('SELECT id, saldo FROM usuarios WHERE usuario = %s', (nombre_usuario,))
    user = cursor.fetchone()

    if not user:
        flash('Usuario no encontrado.')
        return render_template('usuario/pagar_tarjeta.html', mensaje=None)

    if request.method == 'POST':
        tipo_tarjeta = request.form.get('tipo_tarjeta')
        monto_str = request.form.get('monto')

        try:
            monto = float(monto_str)
            saldo_actual = float(user['saldo'])

            if monto > saldo_actual:
                mensaje = "Saldo insuficiente para realizar el pago."
            else:
                nuevo_saldo = saldo_actual - monto
                cursor.execute("UPDATE usuarios SET saldo = %s WHERE id = %s", (nuevo_saldo, user['id']))
                db.commit()
                mensaje = f"Pago realizado con tarjeta {tipo_tarjeta.capitalize()}. Se descontó S/ {monto:.2f}. Saldo restante: S/ {nuevo_saldo:.2f}."

        except ValueError:
            mensaje = "Monto inválido."

    return render_template('usuario/pagar_tarjeta.html', mensaje=mensaje)



@user_bp.route("/ultimos-cambios")
def ultimos_cambios():
    if "usuario" not in session:
        return redirect("/login")

    nombre_usuario = session["usuario"]["usuario"]

    conexion = get_db_connection()
    cursor = conexion.cursor()

    # Obtener usuario_id si no está en la sesión
    cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (nombre_usuario,))
    usuario_id = cursor.fetchone()[0]

    hoy = datetime.now()
    hace_5_dias = hoy - timedelta(days=5)

    cursor.execute("""
        SELECT 'Transferencia Enviada', destinatario, monto, fecha
        FROM transferencias
        WHERE remitente = %s AND fecha >= %s
    """, (nombre_usuario, hace_5_dias))
    transferencias_enviadas = cursor.fetchall()

    cursor.execute("""
        SELECT 'Transferencia Recibida', remitente, monto, fecha
        FROM transferencias
        WHERE destinatario = %s AND fecha >= %s
    """, (nombre_usuario, hace_5_dias))
    transferencias_recibidas = cursor.fetchall()

    cursor.execute("""
        SELECT 'Pago', empresa, monto, fecha
        FROM pagos
        WHERE usuario_id = %s AND fecha >= %s
    """, (usuario_id, hace_5_dias))
    pagos = cursor.fetchall()

    cursor.execute("""
        SELECT 'Préstamo', '', monto, fecha_aprobacion
        FROM prestamos
        WHERE usuario_id = %s AND fecha_aprobacion >= %s
    """, (usuario_id, hace_5_dias))
    prestamos = cursor.fetchall()

    cambios = pagos + prestamos + transferencias_enviadas + transferencias_recibidas
    cambios.sort(key=lambda x: x[3], reverse=True)

    cursor.close()
    conexion.close()

    return render_template("usuario/ultimos_cambios.html", cambios=cambios)

