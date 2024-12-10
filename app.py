import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Función para crear la base de datos y sus tablas
def crear_base_datos():
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    # Crear tabla de materias
    cursor.execute('''CREATE TABLE IF NOT EXISTS materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL
    )''')

    # Crear tabla de estudiantes
    cursor.execute('''CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        contrasena TEXT NOT NULL
    )''')

    # Crear tabla de docentes
    cursor.execute('''CREATE TABLE IF NOT EXISTS docentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        contrasena TEXT NOT NULL,
        materia_id INTEGER,
        FOREIGN KEY (materia_id) REFERENCES materias(id)
    )''')

    # Crear tabla de notas
    cursor.execute('''CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_estudiante INTEGER NOT NULL,
        id_materia INTEGER NOT NULL,
        nota REAL,
        FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id),
        FOREIGN KEY (id_materia) REFERENCES materias(id)
    )''')

    # Insertar materias iniciales
    materias = [
        ('Lenguaje y Comunicación',), ('Matemáticas',), ('Inglés',), ('Física',),
        ('Química',), ('Ciencias Sociales',), ('Música',), ('Religión',),
        ('Artes Plásticas',), ('Psicología',), ('Técnica y Tecnología',)
    ]
    cursor.executemany('INSERT OR IGNORE INTO materias (nombre) VALUES (?)', materias)

    # Insertar estudiantes iniciales
    estudiantes = [
        ('Juan Pérez', 'juan123', 'pass123'), ('María López', 'maria456', 'pass456'),
        ('Carlos García', 'carlos789', 'pass789'), ('Ana Torres', 'ana101', 'pass101'),
        ('Luis Fernández', 'luis202', 'pass202')
    ]
    cursor.executemany('INSERT OR IGNORE INTO estudiantes (nombre, usuario, contrasena) VALUES (?, ?, ?)', estudiantes)

    conn.commit()
    conn.close()


# Página principal
@app.route('/')
def index():
    return render_template('index.html')


# Página de inicio de sesión para estudiantes
@app.route('/login/estudiantes', methods=['GET', 'POST'])
def login_estudiantes():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM estudiantes WHERE usuario = ? AND contrasena = ?', (usuario, contrasena))
        estudiante = cursor.fetchone()
        conn.close()
        
        if estudiante:
            session['usuario'] = usuario
            return redirect(url_for('ver_notas_estudiante'))
        else:
            flash('Credenciales incorrectas. Inténtalo de nuevo.')
    return render_template('login.html', tipo='Estudiantes')


# Página para ver las notas de los estudiantes
@app.route('/notas')
def ver_notas_estudiante():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero.', 'warning')
        return redirect(url_for('login_estudiantes'))

    usuario = session['usuario']

    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    # Obtener las notas del estudiante
    cursor.execute('''
        SELECT m.nombre, n.nota
        FROM materias m
        LEFT JOIN notas n ON m.id = n.id_materia
        JOIN estudiantes e ON e.id = n.id_estudiante
        WHERE e.usuario = ?
    ''', (usuario,))
    notas = cursor.fetchall()
    conn.close()

    return render_template('notas_estudiante.html', usuario=usuario, notas=notas)


# Página para gestionar notas de una materia específica
@app.route('/materia/<nombre_materia>', methods=['GET', 'POST'])
def materia(nombre_materia):
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()

    # Buscar el ID de la materia
    cursor.execute('SELECT id FROM materias WHERE nombre = ?', (nombre_materia,))
    materia = cursor.fetchone()

    if materia:
        materia_id = materia[0]

        if request.method == 'POST':
            # Guardar las notas de los estudiantes
            for estudiante_id, nota in request.form.items():
                if nota:
                    cursor.execute('''
                        INSERT OR REPLACE INTO notas (id_estudiante, id_materia, nota)
                        VALUES (?, ?, ?)
                    ''', (estudiante_id, materia_id, float(nota)))
            conn.commit()

        # Obtener los estudiantes y sus notas
        cursor.execute('''
            SELECT e.id, e.nombre, n.nota
            FROM estudiantes e
            LEFT JOIN notas n ON e.id = n.id_estudiante AND n.id_materia = ?
        ''', (materia_id,))
        estudiantes = cursor.fetchall()
        conn.close()

        return render_template('materia.html', materia=nombre_materia, estudiantes=estudiantes)
    else:
        flash('Materia no encontrada.', 'danger')
        conn.close()
        return redirect(url_for('index'))

@app.route('/docentes')
def docentes():
    return render_template('docentes.html')


@app.route('/modificar_nota/<int:estudiante_id>/<int:materia_id>', methods=['POST'])
def modificar_nota(estudiante_id, materia_id):
    nueva_nota = request.form.get('nota')  # Puedes capturar la nueva nota desde un formulario si lo agregas
    conn = get_db_connection()
    conn.execute('''UPDATE notas SET nota = ? WHERE estudiante_id = ? AND materia_id = ?''', 
                 (nueva_nota, estudiante_id, materia_id))
    conn.commit()
    conn.close()
    return redirect(url_for('gestionar_notas', materia_id=materia_id))  # Redirige a la gestión de notas


if __name__ == '__main__':
    crear_base_datos()  # Crear la base de datos y las tablas si no existen
    app.run(debug=True)