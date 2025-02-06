# Importamos los módulos que necesitamos para la aplicación
from flask import Flask, render_template, request, redirect, url_for, flash,session, jsonify
import os
import mysql.connector
import database as db  # Importamos el archivo database 


# Configuración de la aplicación y conexión a la base de datos
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'supersecretkey'  # Necesario para usar flash messages

def get_db_cursor():
    if not db.database.is_connected():
        db.database.reconnect()
    return db.database.cursor()

# Ruta principal de la aplicación
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('/Pacientes')

#funcion de login
from flask import flash

@app.route('/acceso-login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Verificar si los campos están presentes y no están vacíos
        if 'txtCorreo' not in request.form or 'txtPassword' not in request.form:
            flash("Por favor, ingrese todos los datos.", "error")
            return redirect('/acceso-login')

        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        # Verificar usuario en la base de datos
        cursor = get_db_cursor()
        cursor.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s', (_correo, _password,))
        account = cursor.fetchone()

        if account:
            # Verificar si el usuario tiene el rol adecuado (idRoles = 1)
            idRoles = account[3]  # Asumiendo que 'idRoles' es el nombre de la columna en la base de datos
            if idRoles == 1:
                session['logueado'] = True
                session['idusuarios'] = account[0]
                session['rol'] = 'Administrador' if account[3] == 1 else 'Usuario'
                return render_template('pacientes.html')  # Página principal para usuarios autenticados
            else:
                flash("No tiene permiso para acceder a esta página.", "error")  # Mensaje de error para roles no permitidos
                return redirect('/acceso-login')  # Redirigir a la página de login
        else:
            flash("Correo o contraseña incorrectos.", "error")  # Mensaje de error
            return redirect('/acceso-login')

    return render_template('login.html')  # Página de inicio de sesión para solicitudes GET

@app.route('/logout')
def logout():
    session.clear()  # Elimina todas las variables de sesión
    flash("Has cerrado sesión correctamente.", "success")
    return redirect('/')



# Rutas para la gestión de pacientes
@app.route('/Pacientes', methods=['GET'])
def pacientes():
    cursor = get_db_cursor()    
    cursor.execute("SELECT * FROM pacientes")
    resultado = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in resultado:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('pacientes.html', data=insertObject)

@app.route('/Pacientes/add', methods=['GET','POST'])
def addPacientes():
    if request.method == 'POST':
        try:
            cursor = get_db_cursor()
            Dni = request.form['Dni']
            Nombre = request.form['Nombre']
            Fecha_Nac = request.form['Fecha_Nac']
            Direccion = request.form['Direccion']

            if Dni and Nombre and Fecha_Nac and Direccion:
                sql = "INSERT INTO pacientes (Dni, Nombre, Fecha_Nac, Direccion) VALUES (%s, %s, %s, %s)"
                data = (Dni, Nombre, Fecha_Nac, Direccion)
                cursor.execute(sql, data)
                db.database.commit()
            return redirect(url_for('pacientes'))
        except mysql.connector.Error as e:
            flash(f"Error en la base de datos: {e}")
            return redirect(url_for('pacientes'))
    else:
        return render_template('add_paciente.html')

@app.route('/Pacientes/delete/<string:Dni>')
def delete(Dni):
    cursor = get_db_cursor()
    sql = "DELETE FROM pacientes WHERE Dni=%s"
    data = (Dni,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('pacientes'))

# Vamos a crear la vista para poder editar los registros de nuestra base de datos
@app.route('/Pacientes/edit/<string:Dni>', methods=['GET', 'POST'])
def edit(Dni):
    cursor = get_db_cursor()
    if request.method == 'POST':
        Nombre = request.form['Nombre']
        Fecha = request.form['Fecha_Nac']
        Direccion = request.form['Direccion']

        if Nombre and Fecha and Direccion:
            sql = "UPDATE pacientes SET Nombre = %s, Fecha_Nac = %s, Direccion = %s WHERE Dni = %s"
            data = (Nombre, Fecha, Direccion, Dni)
            cursor.execute(sql, data)
            db.database.commit()
            cursor.close()
            return redirect(url_for('pacientes'))
    else:
        cursor.execute("SELECT * FROM pacientes WHERE Dni=%s", (Dni,))
        paciente = cursor.fetchone()
        cursor.close()
        return render_template('edit.html', paciente=paciente)

#Ruta para clinica
@app.route('/clinicas', methods=['GET', 'POST'])
def mostrarClinicas():
    cursor = get_db_cursor()

# Obtener los médicos para el selector
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            codigo_postal = request.form['Codigo_Postal']
            numero = request.form['Numero']
            calle = request.form['calle']
            telefono = request.form['telefono']
            ciudad = request.form['Ciudad']
            medicooftamologico_NumColegiado = request.form['medicooftamologico_NumColegiado']

            cursor.execute("""
                INSERT INTO clinicas (Codigo_Postal, Numero, calle, telefono, Ciudad, medicooftamologico_NumColegiado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (codigo_postal, numero, calle, telefono, ciudad, medicooftamologico_NumColegiado))
            db.database.commit()
        except mysql.connector.Error as e:
            app.logger.error(f"Error al insertar clínica: {e}")

    cursor.execute("""
        SELECT c.Codigo_Postal, c.Numero, c.calle, c.telefono, c.Ciudad, m.Nombre as Medico
        FROM clinicas c
        JOIN medicooftamologico m ON c.NumColegiado = m.NumColegiado
    """)
    clinicas = [{'Codigo_Postal': row[0], 'Numero': row[1], 'calle': row[2], 'telefono': row[3], 'Ciudad': row[4], 'Medico': row[5]} for row in cursor.fetchall()]

    cursor.close()
    return render_template('clinicas.html', clinicas=clinicas, medico=medico)

@app.route('/clinicas/add', methods=['GET', 'POST'])
def add_clinicas():
    cursor = get_db_cursor()
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Codigo_Postal = request.form['Codigo_Postal']
            Numero = request.form['Numero']
            Calle = request.form['Calle']
            Ciudad = request.form['Ciudad']
            Telefono = request.form['Telefono']
            NumColegiado = request.form['Medico']  # Asegúrate de que este nombre coincida con el del formulario

            if Codigo_Postal and Numero and Calle and Ciudad and Telefono and NumColegiado:
                sql = """INSERT INTO clinicas (Codigo_Postal, Numero, Calle, Ciudad, Telefono, NumColegiado)
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                data = (Codigo_Postal, Numero, Calle, Ciudad, Telefono, NumColegiado)
                cursor.execute(sql, data)
                db.database.commit()
                return redirect(url_for('mostrarClinicas'))
            else:
                flash("Por favor, complete todos los campos.")
        except mysql.connector.Error as e:
            flash(f"Error en la base de datos: {e}")
            return redirect(url_for('mostrarClinicas'))
    else:
        return render_template('add_clinicas.html', medico=medico)



@app.route('/clinicas/delete/<int:Codigo_Postal>')
def delete_clinicas(Codigo_Postal	):
    cursor = get_db_cursor()
    sql = "DELETE FROM clinicas WHERE Codigo_Postal	=%s"
    data = (Codigo_Postal,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('mostrarClinicas'))

@app.route('/clinicas/edit/<int:Codigo_Postal>', methods=['GET', 'POST'])
def edit_clinicas(Codigo_Postal):
    cursor = get_db_cursor()

    # Obtener los médicos para el selector
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Numero = request.form['Numero']
            Calle = request.form['Calle']
            Ciudad = request.form['Ciudad']
            Telefono = request.form['Telefono']
            NumColegiado = request.form['Medico']

            # Validar datos enviados
            if Numero and Calle and Ciudad and Telefono and NumColegiado:
                sql = """
                    UPDATE clinicas
                    SET Numero = %s, Calle = %s, Ciudad = %s, Telefono = %s, NumColegiado = %s
                    WHERE Codigo_Postal=%s
                """
                data = (Numero, Calle, Ciudad, Telefono, NumColegiado, Codigo_Postal)
                cursor.execute(sql, data)
                db.database.commit()
            return redirect(url_for('mostrarClinicas'))
        except mysql.connector.Error as e:
            flash(f"Error en la base de datos: {e}")
            return redirect(url_for('mostrarClinicas'))

    # Para la solicitud GET, obtener los datos de la clínica
    cursor.execute("SELECT * FROM clinicas WHERE Codigo_Postal=%s", (Codigo_Postal,))
    clinica = cursor.fetchone()
    cursor.close()
    return render_template('edit_clinicas.html', clinica=clinica, medicos=medico)


#Ruta para medico
@app.route('/medicooftamologico', methods=['GET'])
def mostrarMedico():
    cursor = get_db_cursor()
    cursor.execute("SELECT * FROM medicooftamologico")
    resultado = cursor.fetchall()
    
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    
    for record in resultado:
        insertObject.append(dict(zip(columnNames, record)))
    
    cursor.close()
    return render_template('medicooftamologico.html', data=insertObject)

@app.route('/medicooftamologico/add', methods=['GET', 'POST'])
def add_medicooftamologico():
    if request.method == 'POST':
        cursor = get_db_cursor()

        try:
            NumColegiado = request.form['NumColegiado']
            Nombre = request.form['Nombre']
            Fecha_Nac = request.form['Fecha_Nac']

            # Depuración: Imprimir los valores recibidos
            # print(f"NumColegiado: {NumColegiado}, Nombre: {Nombre}, Fecha_Nac: {Fecha_Nac}")

            if NumColegiado and Nombre and Fecha_Nac:
                sql = "INSERT INTO medicooftamologico (NumColegiado, Nombre, Fecha_Nac) VALUES (%s, %s, %s)"
                data = (NumColegiado, Nombre, Fecha_Nac)
                cursor.execute(sql, data)
                db.database.commit()
            return redirect(url_for('mostrarMedico'))
        except mysql.connector.Error as e:
            flash(f"Error en la base de datos: {e}")
            return redirect(url_for('mostrarMedico'))
    else:
        return render_template('add_medicooftamologico.html')


@app.route('/medicooftamologico/delete/<string:NumColegiado>')
def delete_medicooftamologico(NumColegiado):
    cursor = get_db_cursor()
    sql = "DELETE FROM medicooftamologico WHERE NumColegiado=%s"
    data = (NumColegiado,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('mostrarMedico'))

@app.route('/medicooftamologico/edit/<string:NumColegiado>', methods=['GET', 'POST'])
def edit_medicooftamologico(NumColegiado):
    cursor = get_db_cursor()
    if request.method == 'POST':
        Nombre = request.form['Nombre']
        Fecha = request.form['Fecha_Nac']

        if Nombre and Fecha:
            sql = "UPDATE medicooftamologico SET Nombre = %s, Fecha_Nac = %s WHERE NumColegiado = %s"
            data = (Nombre, Fecha, NumColegiado)
            cursor.execute(sql, data)
            db.database.commit()
            cursor.close()
            return redirect(url_for('mostrarMedico'))
    else:
        cursor.execute("SELECT * FROM medicooftamologico WHERE NumColegiado=%s", (NumColegiado,))
        medico = cursor.fetchone()
        cursor.close()
        return render_template('editmedicooftamologico.html', medico=medico)
    
#Ruta para periodo
@app.route('/periodo', methods=['GET', 'POST'])
def mostrarPeriodo():
    cursor = get_db_cursor()

    # Obtener los médicos para el selector
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Fecha_I = request.form['Fecha_I']
            Fecha_F = request.form['Fecha_F']
            NumColegiado = request.form['NumColegiado']

            cursor.execute("""
                INSERT INTO periodo (Fecha_I, Fecha_F,NumColegiado)
                VALUES (%s, %s, %s)
            """, (Fecha_I, Fecha_F,NumColegiado))
            db.database.commit()
        except mysql.connector.Error as e:
            app.logger.error(f"Error al insertar clínica: {e}")

    cursor.execute("""
        SELECT c.Fecha_I, c.Fecha_F, m.Nombre as Medico
        FROM periodo c
        JOIN medicooftamologico m ON c.NumColegiado = m.NumColegiado
    """)
    periodo = [{'Fecha_I': row[0], 'Fecha_F': row[1], 'Medico': row[2]} for row in cursor.fetchall()]

    cursor.close()
    return render_template('periodo.html', periodo=periodo, medico=medico)

@app.route('/periodo/add', methods=['GET', 'POST'])
def add_periodo():
    cursor = get_db_cursor()
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Fecha_I = request.form['Fecha_I']
            Fecha_F = request.form['Fecha_F']
            NumColegiado = request.form['Medico']  # Asegúrate de que este nombre coincida con el del formulario

            if Fecha_I and Fecha_F and NumColegiado:
                sql = """INSERT INTO periodo (Fecha_I, Fecha_F, NumColegiado)
                         VALUES (%s, %s, %s)"""
                data = (Fecha_I, Fecha_F, NumColegiado)
                cursor.execute(sql, data)
                db.database.commit()
                return redirect(url_for('mostrarPeriodo'))
            else:
                flash("Por favor, complete todos los campos.")
        except mysql.connector.Error as e:
            flash(f"Error en la base de datos: {e}")
            return redirect(url_for('mostrarPeriodo'))
    else:
        return render_template('add_periodo.html', medico=medico)



from datetime import datetime

@app.route('/periodo/delete/<Fecha_I>/<Fecha_F>', methods=['GET', 'POST'])
def delete_periodo(Fecha_I, Fecha_F):
    try:
        # Convertir los parámetros de la URL en objetos de fecha
        Fecha_I_obj = datetime.strptime(Fecha_I, "%Y-%m-%d").date()
        Fecha_F_obj = datetime.strptime(Fecha_F, "%Y-%m-%d").date()

        cursor = get_db_cursor()
        sql = "DELETE FROM periodo WHERE Fecha_I = %s AND Fecha_F = %s"
        data = (Fecha_I_obj, Fecha_F_obj)
        cursor.execute(sql, data)
        db.database.commit()
        flash("Periodo eliminado correctamente.", "success")
    except ValueError:
        flash("Formato de fecha inválido. Use el formato YYYY-MM-DD.", "danger")
    except mysql.connector.Error as e:
        flash(f"Error al eliminar el periodo: {e}", "danger")
    return redirect(url_for('mostrarPeriodo'))


from datetime import datetime
from flask import request, redirect, url_for, flash, render_template

@app.route('/periodo/edit/<Fecha_I>/<Fecha_F>', methods=['GET', 'POST'])
def edit_periodo(Fecha_I, Fecha_F):
    cursor = get_db_cursor()
    try:
        # Convertir las fechas de la URL a objetos datetime
        Fecha_I_obj = datetime.strptime(Fecha_I, "%Y-%m-%d").date()
        Fecha_F_obj = datetime.strptime(Fecha_F, "%Y-%m-%d").date()

        # Obtener los médicos para el selector
        cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
        medicos = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

        if request.method == 'POST':
            try:
                NumColegiado = request.form['Medico']

                # Validar datos enviados
                if NumColegiado:
                    sql = """
                        UPDATE periodo
                        SET NumColegiado = %s
                        WHERE Fecha_I = %s AND Fecha_F = %s
                    """
                    data = (NumColegiado, Fecha_I_obj, Fecha_F_obj)
                    cursor.execute(sql, data)
                    db.database.commit()
                    flash("Periodo actualizado correctamente.", "success")
                return redirect(url_for('mostrarPeriodo'))
            except mysql.connector.Error as e:
                flash(f"Error en la base de datos: {e}", "danger")
                return redirect(url_for('mostrarPeriodo'))

        # Para la solicitud GET, obtener los datos del período
        cursor.execute("SELECT * FROM periodo WHERE Fecha_I = %s AND Fecha_F = %s", (Fecha_I_obj, Fecha_F_obj))
        periodo = cursor.fetchone()
        return render_template('edit_periodo.html', periodo=periodo, medicos=medicos)

    finally:
        cursor.close()

#Ruta para prueba
@app.route('/prueba', methods=['GET', 'POST'])
def mostrarPrueba():
    cursor = get_db_cursor()

    # Obtener los médicos para el selector
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    # Obtener los pacientes para el selector
    cursor.execute("SELECT Id, Nombre FROM tratamiento")
    tratamiento = [{'Id': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Codigo_Prueba = request.form['Codigo_Prueba']
            Nombre = request.form['Nombre']
            Fecha = request.form['Fecha']
            Hora = request.form['Hora']
            Tipo = request.form['Tipo']
            Descripcion = request.form['Descripcion']
            tratamiento = request.form['tratamiento_Id']
            medicooftamologico_NumColegiado = request.form['medicooftamologico_NumColegiado']

            cursor.execute("""
                INSERT INTO prueba (Codigo_Prueba, Nombre, Fecha, Hora, Tipo, Descripcion, Id, medicooftamologico_NumColegiado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (Codigo_Prueba, Nombre, Fecha, Hora, Tipo, Descripcion, tratamiento, medicooftamologico_NumColegiado))
            db.database.commit()
        except mysql.connector.Error as e:
            app.logger.error(f"Error al insertar prueba: {e}")

    cursor.execute("""
        SELECT p.Codigo_Prueba, p.Nombre, p.Fecha, p.Hora, p.Tipo, p.Descripcion, pa.Nombre AS tratamiento, m.Nombre AS Medico
        FROM prueba p
        JOIN tratamiento pa ON p.Id = pa.Id
        JOIN medicooftamologico m ON p.NumColegiado = m.NumColegiado
    """)
    pruebas = [
        {
            'Codigo_Prueba': row[0],
            'Nombre': row[1],
            'Fecha': row[2],
            'Hora': row[3],
            'Tipo': row[4],
            'Descripcion': row[5],
            'tratamiento': row[6],
            'Medico': row[7]
        } for row in cursor.fetchall()
    ]

    cursor.close()
    return render_template('prueba.html', pruebas=pruebas, medico=medico, tratamiento=tratamiento)


@app.route('/prueba/add', methods=['GET', 'POST'])
def add_prueba():
    cursor = get_db_cursor()
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    cursor.execute("SELECT Id, Nombre FROM tratamiento")
    tratamiento = [{'Id': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Codigo_Prueba = request.form['Codigo_Prueba']
            Nombre = request.form['Nombre']
            Fecha = request.form['Fecha']
            Hora = request.form['Hora']
            Tipo = request.form['Tipo']
            Descripcion = request.form['Descripcion']
            tratamiento_id = request.form['tratamiento']  # Renombrado para evitar conflicto de nombres
            NumColegiado = request.form['Medico']

            if Codigo_Prueba and Nombre and Fecha and Hora and Tipo and Descripcion and tratamiento_id and NumColegiado:
                sql = """INSERT INTO prueba (Codigo_Prueba, Nombre, Fecha, Hora, Tipo, Descripcion, Id, NumColegiado)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""  # Corrección de tabla y columnas
                data = (Codigo_Prueba, Nombre, Fecha, Hora, Tipo, Descripcion, tratamiento_id, NumColegiado)
                cursor.execute(sql, data)
                db.database.commit()
                return redirect(url_for('mostrarPrueba'))
            else:
                flash("Por favor, complete todos los campos.")
        except mysql.connector.Error as e:
            flash(f"Error en la base de datos: {e}")
            return redirect(url_for('mostrarPrueba'))
    else:
        return render_template('add_prueba.html', tratamiento=tratamiento, medico=medico)



@app.route('/prueba/delete/<int:Codigo_Prueba>')
def delete_prueba(Codigo_Prueba    ):
    cursor = get_db_cursor()
    sql = "DELETE FROM prueba WHERE Codigo_Prueba	=%s"
    data = (Codigo_Prueba,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('mostrarPrueba'))

@app.route('/prueba/edit/<int:Codigo_Prueba>', methods=['GET', 'POST'])
def edit_prueba(Codigo_Prueba):
    cursor = get_db_cursor()

    # Obtener los médicos para el selector
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medicos = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    # Obtener los pacientes para el selector
    cursor.execute("SELECT Id, Nombre FROM tratamiento")
    tratamiento = [{'Id': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Nombre = request.form['Nombre']
            Fecha = request.form['Fecha']
            Hora = request.form['Hora']
            Tipo = request.form['Tipo']
            Descripcion = request.form['Descripcion']
            Id = request.form['tratamiento']
            NumColegiado = request.form['Medico']

            # Validar datos enviados
            if Nombre and Fecha and Hora and Tipo and Descripcion and Id and NumColegiado:
                sql = """
                    UPDATE prueba
                    SET Nombre = %s, Fecha = %s, Hora = %s, Tipo = %s, Descripcion = %s, Id = %s, NumColegiado = %s
                    WHERE Codigo_Prueba=%s
                """
                data = (Nombre, Fecha, Hora, Tipo, Descripcion, Id, NumColegiado, Codigo_Prueba)
                cursor.execute(sql, data)
                db.database.commit()
            return redirect(url_for('mostrarPrueba'))
        except mysql.connector.Error as e:
            flash(f"Error en la base de datos: {e}")
            return redirect(url_for('mostrarPrueba'))

    # Para la solicitud GET, obtener los datos de la clínica
    cursor.execute("SELECT * FROM prueba WHERE Codigo_Postal=%s", (Codigo_Prueba,))
    prueba = cursor.fetchone()
    cursor.close()
    return render_template('edit_prueba.html', prueba=prueba, tratamiento=tratamiento, medicos=medicos)

#Ruta para tratamiento
@app.route('/tratamiento', methods=['GET', 'POST'])
def mostrarTratamiento():
    cursor = get_db_cursor()

    # Obtener los médicos para el selector
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    # Obtener los pacientes para el selector
    cursor.execute("SELECT Dni, Nombre FROM pacientes")
    pacientes = [{'Dni': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Id = request.form['Id']
            Nombre = request.form['Nombre']
            Fecha_Inicio = request.form['Fecha_Inicio']
            pacientes_Dni = request.form['pacientes_Dni']
            NumColegiado = request.form['NumColegiado']

            cursor.execute("""
                INSERT INTO tratamiento (Id, Nombre, Fecha_Inicio, NumColegiado, Dni)
                VALUES (%s, %s, %s, %s, %s)
            """, (Id, Nombre, Fecha_Inicio, pacientes_Dni, NumColegiado))
            db.database.commit()
        except mysql.connector.Error as e:
            app.logger.error(f"Error al insertar tratamiento: {e}")

    cursor.execute("""
        SELECT 
            t.Id, 
            t.Nombre, 
            t.Fecha_Inicio, 
            pa.Nombre AS paciente,  
            m.Nombre AS Medico
        FROM 
            tratamiento t
        JOIN 
            pacientes pa ON t.Dni = pa.Dni
        JOIN 
            medicooftamologico m ON t.NumColegiado = m.NumColegiado
    """)

    tratamientos = [
        {
            'Id': row[0],
            'Nombre': row[1],
            'Fecha_Inicio': row[2],
            'paciente': row[3], 
            'Medico': row[4]
        } for row in cursor.fetchall()
    ]

    cursor.close()
    return render_template('tratamiento.html', tratamientos=tratamientos, medico=medico, pacientes=pacientes)

@app.route('/search', methods=['POST'])
def search():
    cursor = get_db_cursor()
    search_term = request.form.get('search', '').lower()

    # Consulta con filtros dinámicos usando LIKE
    sql = """
        SELECT 
            t.Id, 
            t.Nombre, 
            t.Fecha_Inicio, 
            pa.Nombre AS paciente,  
            m.Nombre AS Medico
        FROM 
            tratamiento t
        JOIN 
            pacientes pa ON t.Dni = pa.Dni
        JOIN 
            medicooftamologico m ON t.NumColegiado = m.NumColegiado
        WHERE 
            LOWER(t.Nombre) LIKE %s OR
            LOWER(pa.Nombre) LIKE %s OR
            LOWER(m.Nombre) LIKE %s
    """
    # Formatea el término de búsqueda para LIKE
    like_term = f"%{search_term}%"
    cursor.execute(sql, (like_term, like_term, like_term))

    # Procesa los resultados
    results = [
        {
            'Id': row[0],
            'Nombre': row[1],
            'Fecha_Inicio': row[2],
            'paciente': row[3],
            'Medico': row[4]
        } for row in cursor.fetchall()
    ]

    cursor.close()
    return jsonify(results)



@app.route('/tratamiento/add', methods=['GET', 'POST'])
def add_tratamiento():
    cursor = get_db_cursor()
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    cursor.execute("SELECT Dni, Nombre FROM pacientes")
    pacientes = [{'Dni': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Id = request.form['Id']
            Nombre = request.form['Nombre']
            Fecha_Inicio = request.form['Fecha_Inicio']
            NumColegiado = request.form['Medico']
            pacientes_Dni = request.form['paciente']

            if Id and Nombre and Fecha_Inicio  and NumColegiado and pacientes_Dni:
                sql = """INSERT INTO tratamiento (Id, Nombre, Fecha_Inicio, NumColegiado, Dni)
                         VALUES (%s, %s, %s, %s, %s)"""
                data = (Id, Nombre, Fecha_Inicio, NumColegiado, pacientes_Dni)
                cursor.execute(sql, data)
                db.database.commit()
                return redirect(url_for('mostrarTratamiento'))
            else:
                flash("Por favor, complete todos los campos.")
        except mysql.connector.Error as e:
            flash(f"Error en la base de datos: {e}")
            return redirect(url_for('mostrarTratamiento'))
    else:
        return render_template('add_tratamiento.html', pacientes=pacientes, medico=medico)

@app.route('/tratamiento/delete/<int:Id>')
def delete_tratamiento(Id):
    cursor = get_db_cursor()
    sql = "DELETE FROM tratamiento WHERE Id=%s"
    data = (Id,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('mostrarTratamiento'))

@app.route('/tratamiento/edit/<int:Id>', methods=['GET', 'POST'])
def edit_tratamiento(Id):
    cursor = get_db_cursor()

    # Obtener los médicos para el selector
    cursor.execute("SELECT NumColegiado, Nombre FROM medicooftamologico")
    medico = [{'NumColegiado': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    cursor.execute("SELECT Dni, Nombre FROM pacientes")
    pacientes = [{'Dni': row[0], 'Nombre': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        try:
            Nombre = request.form['Nombre']
            Fecha_Inicio = request.form['Fecha_Inicio']
            NumColegiado = request.form['Medico']
            pacientes_Dni = request.form['paciente']

            # Validar datos enviados
            if Nombre and Fecha_Inicio and NumColegiado and pacientes_Dni:
                sql = """
                    UPDATE tratamiento
                    SET Nombre = %s, Fecha_Inicio = %s,  NumColegiado = %s, Dni = %s
                    WHERE Id=%s
                """
                data = (Nombre, Fecha_Inicio, NumColegiado, pacientes_Dni, Id)
                cursor.execute(sql, data)
                db.database.commit()
            return redirect(url_for('mostrarTratamiento'))
        except mysql.connector.Error as e:
            flash(f"Error en la base de datos: {e}")
            return redirect(url_for('mostrarTratamiento'))

    # Para la solicitud GET, obtener los datos del tratamiento
    cursor.execute("SELECT * FROM tratamiento WHERE Id=%s", (Id,))
    tratamiento = cursor.fetchone()
    cursor.close()
    return render_template('edit_tratamiento.html',tratamiento=tratamiento, pacientes=pacientes, medico=medico)


if __name__ == '__main__':
    app.run(debug=True, port=4000)
