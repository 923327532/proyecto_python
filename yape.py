from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from config import get_db_connection
import qrcode
import base64
from io import BytesIO

yape_bp = Blueprint('yape', __name__, url_prefix='/yape')

@yape_bp.route('/')
def yape_opciones():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session['usuario']['usuario']

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT telefono FROM yape_usuarios WHERE usuario = %s", (usuario,))
    result = cursor.fetchone()
    telefono = result[0] if result else None
    cursor.close()
    db.close()

    return render_template('usuario/opciones_yape.html', telefono=telefono)

@yape_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_yape():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session['usuario']['usuario']
    exito = False

    if request.method == 'POST':
        telefono = request.form['telefono'].strip()

        if len(telefono) != 9 or not telefono.isdigit():
            flash("El número debe tener 9 dígitos", "error")
            return redirect(url_for('yape.registrar_yape'))

        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO yape_usuarios (usuario, telefono) VALUES (%s, %s)", (usuario, telefono))
            db.commit()
            exito = True
        except Exception as e:
            db.rollback()
            flash(f"Error: {e}", "error")
        finally:
            cursor.close()
            db.close()

    return render_template('usuario/registrar_yape.html', exito=exito)

@yape_bp.route('/enviar', methods=['GET', 'POST'])
def enviar_yape():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    remitente = session['usuario']['usuario']
    telefono_prefill = request.args.get('telefono', '')

    if request.method == 'POST':
        telefono_destino = request.form['telefono']
        monto = float(request.form['monto'])

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT usuario FROM yape_usuarios WHERE telefono = %s", (telefono_destino,))
        receptor_data = cursor.fetchone()
        if not receptor_data:
            flash("Número no registrado en Yape", "error")
            return redirect(url_for('yape.enviar_yape'))

        destinatario = receptor_data[0]

        # Validar saldo
        cursor.execute("SELECT saldo FROM usuarios WHERE usuario = %s", (remitente,))
        saldo_data = cursor.fetchone()

        if not saldo_data:
            flash("No se encontró tu cuenta.", "error")
            return redirect(url_for('yape.enviar_yape'))

        saldo = saldo_data[0]

        if saldo < monto:
            flash(f"No tienes saldo suficiente para yapear. Tu saldo actual es: S/ {saldo:.2f}", "error")
            return redirect(url_for('yape.enviar_yape'))

        try:
            cursor.execute("UPDATE usuarios SET saldo = saldo - %s WHERE usuario = %s", (monto, remitente))
            cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE usuario = %s", (monto, destinatario))
            cursor.execute("INSERT INTO transferencias_yape (remitente, destinatario, monto, fecha) VALUES (%s, %s, %s, NOW())", (remitente, destinatario, monto))
            db.commit()
            flash("Transferencia exitosa por Yape", "success")
        except Exception as e:
            db.rollback()
            flash(f"Error: {e}", "error")
        finally:
            cursor.close()
            db.close()

        return redirect(url_for('user.usuario_home'))


    return render_template('usuario/enviar_yape.html', telefono_prefill=telefono_prefill)

@yape_bp.route('/escanear_qr')
def escanear_qr():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    return render_template('usuario/escanear_yape.html')

@yape_bp.route('/generar_qr')
def generar_qr():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session['usuario']['usuario']

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT telefono FROM yape_usuarios WHERE usuario = %s", (usuario,))
    result = cursor.fetchone()
    cursor.close()
    db.close()

    if not result:
        flash("Debes registrar tu número Yape primero.", "error")
        return redirect(url_for('yape.registrar_yape'))

    telefono = result[0]

    qr = qrcode.make(telefono)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()

    return render_template('usuario/generar_qr.html', qr_base64=qr_base64, telefono=telefono)

@yape_bp.route('/historial', methods=['GET', 'POST'])
def historial_yape():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = session['usuario']['usuario']
    filtro_tipo = request.form.get('filtro_tipo', 'enviados')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    db = get_db_connection()
    cursor = db.cursor()

    query = """
        SELECT remitente, destinatario, monto, fecha
        FROM transferencias_yape
        WHERE
    """
    params = []

    if filtro_tipo == 'enviados':
        query += " remitente = %s"
        params.append(usuario)
    elif filtro_tipo == 'recibidos':
        query += " destinatario = %s"
        params.append(usuario)

    # Agregar condiciones de fecha si existen
    if fecha_inicio:
        query += " AND fecha >= %s"
        params.append(f"{fecha_inicio} 00:00:00")
    if fecha_fin:
        query += " AND fecha <= %s"
        params.append(f"{fecha_fin} 23:59:59")

    query += " ORDER BY fecha DESC"

    cursor.execute(query, tuple(params))
    movimientos = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('usuario/historial_yape.html',
                           movimientos=movimientos,
                           filtro_tipo=filtro_tipo,
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin)
