from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from config import get_db_connection
from correo import enviar_correo
from colas import cola
from psycopg2.extras import RealDictCursor



admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def validar_admin():
    return 'usuario' in session and session['usuario']['perfil'] == 'admin'

@admin_bp.route('/')
def admin_home():
    if not validar_admin():
        return redirect(url_for('login'))

    ocultar = set(session.get('ocultar', []))  

    db = get_db_connection()
    cursor = db.cursor()

    consultas = {
        'transferencias': {
            'query': "SELECT remitente, destinatario, monto, fecha FROM transferencias ORDER BY fecha DESC",
            'variable': 'transferencias',
        },
        'pagos': {
            'query': "SELECT usuario, descripcion, monto, fecha FROM pagos ORDER BY fecha DESC",
            'variable': 'pagos',
        },
        'mensajes': {
            'query': "SELECT id, usuario, mensaje, respuesta, fecha FROM mensajes ORDER BY fecha DESC",
            'variable': 'mensajes',
        },
    }

    datos = {}
    for key, item in consultas.items():
        if key in ocultar:
            datos[item['variable']] = []
        else:
            cursor.execute(item['query'])
            datos[item['variable']] = cursor.fetchall()

    cursor.execute("SELECT id, usuario, monto, meses, cuota, estado, fecha FROM prestamos ORDER BY fecha DESC")
    prestamos = cursor.fetchall()
    cursor.execute("SELECT * FROM solicitudes_tarjetas ORDER BY id DESC")
    solicitudes_resumen = cursor.fetchall()
    cola_actual = [] if 'cola' in ocultar else cola.mostrar()

    cursor.close()
    db.close()

    return render_template('admin/admin.html',
                       transferencias=datos.get('transferencias', []),
                       pagos=datos.get('pagos', []),
                       mensajes=datos.get('mensajes', []),
                       prestamos=prestamos,
                       solicitudes_resumen=solicitudes_resumen,
                       cola=cola_actual,
                       transferencias_ocultos='transferencias' in ocultar,
                       pagos_ocultos='pagos' in ocultar,
                       mensajes_ocultos='mensajes' in ocultar,
                       cola_ocultos='cola' in ocultar)


@admin_bp.route('/aprobar_prestamo/<int:id>')
def aprobar_prestamo(id):
    if 'usuario' in session and session['usuario']['perfil'] == 'admin':
        db = get_db_connection()
        cursor = db.cursor()

        # Obtener el usuario y el monto del préstamo
        cursor.execute("SELECT usuario, monto FROM prestamos WHERE id=%s", (id,))
        prestamo = cursor.fetchone()
        usuario = prestamo[0]
        monto = prestamo[1]

        cursor.execute("UPDATE prestamos SET estado='Aprobado' WHERE id=%s", (id,))
        cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE usuario = %s", (monto, usuario))

        db.commit()
        cursor.close()
        db.close()

        mensaje = f"""
        <h3>Préstamo aprobado en Banco TECSUP</h3>
        <p>Hola <strong>{usuario}</strong>,</p>
        <p>Tu solicitud de préstamo por un monto de <strong>S/. {monto}</strong> ha sido <strong>aprobada</strong> y el monto fue depositado en tu cuenta.</p>
        <p>Gracias por confiar en nosotros.</p>
        """
        enviar_correo(usuario, "Tu préstamo ha sido aprobado", mensaje)

        return redirect(url_for('admin.ver_solicitudes_prestamos'))

    return redirect(url_for('login'))



@admin_bp.route('/rechazar_prestamo/<int:id>')
def rechazar_prestamo(id):
    if 'usuario' in session and session['usuario']['perfil'] == 'admin':
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT usuario, monto FROM prestamos WHERE id=%s", (id,))
        prestamo = cursor.fetchone()
        usuario = prestamo[0]
        monto = prestamo[1]
        cursor.execute("UPDATE prestamos SET estado='Rechazado' WHERE id=%s", (id,))
        db.commit()

        cursor.close()
        db.close()

        from correo import enviar_correo  
        mensaje = f"""
        <h3>Préstamo Rechazado - Banco TECSUP</h3>
        <p>Hola <strong>{usuario}</strong>, lamentamos informarte que tu solicitud de préstamo por <strong>S/. {monto}</strong> ha sido rechazada.</p>
        <p>Gracias por confiar en nosotros.</p>
        """
        enviar_correo(usuario, "Préstamo rechazado", mensaje)

        return redirect(url_for('admin.ver_solicitudes_prestamos'))
    return redirect(url_for('login'))
 
@admin_bp.route('/actualizar_solicitud/<int:solicitud_id>/<accion>')
def actualizar_solicitud(solicitud_id, accion):
    if 'usuario' not in session or session['usuario']['perfil'] != 'admin':
        return redirect(url_for('login'))

    estado = 'aprobado' if accion == 'aprobar' else 'rechazado'

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE solicitudes_tarjetas SET estado = %s WHERE id = %s", (estado, solicitud_id))
    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin.ver_solicitudes'))

@admin_bp.route('/ver_solicitudes')
def ver_solicitudes():
    if 'usuario' not in session or session['usuario']['perfil'] != 'admin':
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM solicitudes_tarjetas")
    solicitudes = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('admin/ver_solicitudes.html', solicitudes=solicitudes)

@admin_bp.route('/responder_mensaje/<int:mensaje_id>', methods=['POST'])
def responder_mensaje(mensaje_id):
    if 'usuario' in session and session['usuario']['perfil'] == 'admin':
        respuesta = request.form['respuesta']
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("UPDATE mensajes SET respuesta = %s WHERE id = %s", (respuesta, mensaje_id))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin.admin_home'))
    return redirect(url_for('login'))

@admin_bp.route('/ver_cola')
def ver_cola():
    if 'usuario' not in session or session['usuario']['perfil'] != 'admin':
        return redirect(url_for('login'))

    return f"Clientes en cola: {cola.mostrar()}"

@admin_bp.route('/atender_cliente')
def atender_cliente():
    if 'usuario' not in session or session['usuario']['perfil'] != 'admin':
        return redirect(url_for('login'))

    cliente = cola.desencolar()
    if cliente:
        return f"Estás atendiendo a: {cliente}"
    else:
        return "No hay clientes en espera."

@admin_bp.route('/gestionar_cola')
def gestionar_cola():
    if 'usuario' not in session or session['usuario']['perfil'] != 'admin':
        return redirect(url_for('login'))
    
    clientes = []
    actual = cola.frente
    while actual is not None:
        clientes.append(actual.dato)
        actual = actual.siguiente
    
    return render_template('admin/gestionar_cola.html', clientes=clientes)

@admin_bp.route('/despachar_cliente')
def despachar_cliente():
    if 'usuario' not in session or session['usuario']['perfil'] != 'admin':
        return redirect(url_for('login'))

    cliente = cola.desencolar()
    return redirect(url_for('admin.gestionar_cola'))

@admin_bp.route('/ver_solicitudes_prestamos')
def ver_solicitudes_prestamos():
    if 'usuario' not in session or session['usuario']['perfil'] != 'admin':
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM prestamos ORDER BY fecha DESC")
    prestamos = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('admin/ver_solicitudes_prestamos.html', prestamos=prestamos)


@admin_bp.route('/limpiar_historial', methods=['POST'])
def limpiar_historial():
    tipo = request.form.get('tipo')

    if tipo not in ['pagos', 'transferencias', 'mensajes', 'cola']:
        flash("Tipo de historial no reconocido.", "danger")
        return redirect(url_for('admin.admin_home'))

    # Guardamos en sesión qué tipo se va a ocultar
    if 'ocultar' not in session:
        session['ocultar'] = []

    if tipo not in session['ocultar']:
        session['ocultar'].append(tipo)

    flash(f"Historial de {tipo} ocultado temporalmente.", "success")
    return redirect(url_for('admin.admin_home'))

@admin_bp.route('/actualizar_cambio', methods=['GET', 'POST'])
def actualizar_cambio():
    db = get_db_connection()
    cursor = db.cursor()
    mensaje = None

    if request.method == 'POST':
        nuevo_dolar = float(request.form['nuevo_dolar'])

        cursor.execute("UPDATE tipo_cambio SET valor = %s WHERE tipo = 'USD_PEN'", (nuevo_dolar,))
        db.commit()
        mensaje = f"Tipo de cambio actualizado a {nuevo_dolar}"

    cursor.execute("SELECT valor FROM tipo_cambio WHERE tipo = 'USD_PEN'")
    valor_actual = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return render_template('admin/actualizar_cambio.html', valor_actual=valor_actual, mensaje=mensaje)

@admin_bp.route('/mostrar_historial', methods=['POST'])
def mostrar_historial():
    tipo = request.form.get('tipo')
    ocultar = session.get('ocultar', [])
    if tipo in ocultar:
        ocultar.remove(tipo)
        session['ocultar'] = ocultar
        session.modified = True
        flash(f"Historial de {tipo} restaurado.", "success")
    return redirect(url_for('admin.admin_home'))

@admin_bp.route('/historial_yape_admin', methods=['GET', 'POST'])
def historial_yape_admin():
    if 'usuario' not in session or session['usuario']['perfil'] != 'admin':
        return redirect(url_for('login'))

    # Filtrado similar, pero sin limitar al usuario
    filtro_tipo = request.form.get('filtro_tipo', 'todos')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    db = get_db_connection()
    cursor = db.cursor()

    query = "SELECT remitente, destinatario, monto, fecha FROM transferencias_yape WHERE 1=1"
    params = []

    if filtro_tipo == 'enviados':
        query += " AND remitente IS NOT NULL"
    elif filtro_tipo == 'recibidos':
        query += " AND destinatario IS NOT NULL"

    if fecha_inicio:
        query += " AND fecha >= %s"
        params.append(f"{fecha_inicio} 00:00:00")
    if fecha_fin:
        query += " AND fecha <= %s"
        params.append(f"{fecha_fin} 23:59:59")

    query += " ORDER BY fecha DESC"
    cursor.execute(query, tuple(params))
    movimientos = cursor.fetchall()

    # Exportar si se solicitó
    if request.form.get('exportar') == 'excel':
        import pandas as pd
        from flask import send_file
        from io import BytesIO

        df = pd.DataFrame(movimientos, columns=["Remitente", "Destinatario", "Monto", "Fecha"])
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='HistorialYape')
        output.seek(0)
        return send_file(output, download_name='historial_yape_admin.xlsx',
                         as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    cursor.close()
    db.close()

    return render_template('admin/historial_yape_admin.html',
                           movimientos=movimientos,
                           filtro_tipo=filtro_tipo,
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin)
