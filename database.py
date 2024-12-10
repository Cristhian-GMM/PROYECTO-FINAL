import sqlite3

def init_db():
    try:
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()

        # Crear tabla para estudiantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL
            )
        ''')

        # Crear tabla para docentes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS docentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                materia TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL
            )
        ''')

        # Insertar datos en la tabla de estudiantes (no necesitamos la columna 'id' ya que es autoincremental)
        cursor.execute('INSERT OR IGNORE INTO estudiantes (nombre, usuario, contrasena) VALUES (?, ?, ?)',
                       ('Juan Pérez', 'estudiante1', '12345'))
        cursor.execute('INSERT OR IGNORE INTO estudiantes (nombre, usuario, contrasena) VALUES (?, ?, ?)',
                       ('Ana García', 'estudiante2', '67890'))

        # Insertar datos en la tabla de docentes (no necesitamos la columna 'id' ya que es autoincremental)
        cursor.execute('INSERT OR IGNORE INTO docentes (nombre, materia, usuario, contrasena) VALUES (?, ?, ?, ?)',
                       ('María López', 'Matemáticas', 'docente1', '67890'))
        cursor.execute('INSERT OR IGNORE INTO docentes (nombre, materia, usuario, contrasena) VALUES (?, ?, ?, ?)',
                       ('Carlos Ramírez', 'Física', 'docente2', '12345'))

        conn.commit()
        print("Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        print("Error al inicializar la base de datos:", e)
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()