from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui' 

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Ruta al archivo JSON
DATA_FILE = 'desayunos.json'

# Cargar datos de desayunos
def cargar_desayunos():
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

# Ruta principal (usa base.html)
@app.route('/')
def home():
    return render_template('base.html')

# Ruta para clientes (muestra desayunos)
def cargar_desayunos():
    with open('desayunos.json', 'r', encoding='utf-8') as file:
        return json.load(file)  # Devuelve un diccionario con los datos

# Ruta para clientes
@app.route('/clientes')
def clientes():
    desayunos = cargar_desayunos()
    return render_template('clientes.html', desayunos=desayunos)

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('usuario') == 'Jime1506' and request.form.get('contrasena') == 'JimeTita1506':
        session['admin_logueado'] = True  # Marcar como autenticado
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('home'))  # Redirige si falla

# Ruta del panel admin (protegida)
@app.route('/admin')
def admin():
    if not session.get('admin_logueado'):
        return redirect(url_for('home'))  # Bloquea acceso no autorizado
    
    return render_template('admin.html')

# Ruta para logout
@app.route('/logout')
def logout():
    session.pop('admin_logueado', None)
    return redirect(url_for('home'))

@app.route('/admin/editar/<tipo>')
def editar_desayuno(tipo):
    if not session.get('admin_logueado'):
        return redirect(url_for('home'))
    
    desayunos = cargar_desayunos()
    desayuno = desayunos.get(tipo)
    
    if not desayuno:
        return redirect(url_for('admin'))
    
    return render_template('editar_desayuno.html', desayuno=desayuno, tipo=tipo)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = 'static/img/star/'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_desayunos(data):
    with open('desayunos.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

@app.route('/admin/editar/STAR', methods=['GET', 'POST'])
def editar_star():
    if not session.get('admin_logueado'):
        return redirect(url_for('home'))

    desayunos = cargar_desayunos()
    desayuno = desayunos['STAR']

    if request.method == 'POST':
        # Procesar imágenes subidas
        nuevas_imagenes = []
        for i in range(1, 4):
            file_key = f'imagen_{i}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"star_{i}.jpg")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    nuevas_imagenes.append(filename)

        # Procesar imagen menú
        menu_file = request.files['imagen_menu']
        if menu_file and allowed_file(menu_file.filename):
            menu_filename = secure_filename("menu_star.jpg")
            menu_file.save(os.path.join(app.config['UPLOAD_FOLDER'], menu_filename))
            desayuno['imagen_menu'] = menu_filename

        # Actualizar precio
        desayuno['precio'] = float(request.form['precio'])
        
        # Guardar cambios
        guardar_desayunos(desayunos)
        flash('¡Cambios guardados exitosamente!', 'success')
        return redirect(url_for('editar_star'))

    return render_template('editar_star.html', desayuno=desayuno)

# Configuración de carpetas para VIP y DETALLE
app.config['UPLOAD_FOLDER_VIP'] = 'static/img/vip/'
app.config['UPLOAD_FOLDER_DETALLE'] = 'static/img/detalle/'

# Ruta para editar VIP
@app.route('/admin/editar/VIP', methods=['GET', 'POST'])
def editar_vip():
    if not session.get('admin_logueado'):
        return redirect(url_for('home'))

    desayunos = cargar_desayunos()
    desayuno = desayunos['VIP']

    if request.method == 'POST':
        # Procesar imágenes (igual que en editar_star, pero con carpeta VIP)
        nuevas_imagenes = desayuno['imagenes']
        for i in range(3):
            file_key = f'imagen_{i+1}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"vip_{i+1}.jpg")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER_VIP'], filename))
                    nuevas_imagenes[i] = filename

        # Procesar menú y precio (igual que STAR)
        menu_file = request.files['imagen_menu']
        if menu_file and allowed_file(menu_file.filename):
            menu_filename = secure_filename("menu_vip.jpg")
            menu_file.save(os.path.join(app.config['UPLOAD_FOLDER_VIP'], menu_filename))
            desayuno['imagen_menu'] = menu_filename

        desayuno['precio'] = float(request.form['precio'])
        guardar_desayunos(desayunos)
        flash('¡VIP actualizado!', 'success')
        return redirect(url_for('editar_vip'))

    return render_template('editar_vip.html', desayuno=desayuno)

# Ruta para editar CON DETALLE (copia de VIP, cambiando las rutas)
@app.route('/admin/editar/CONDETALLE', methods=['GET', 'POST'])
def editar_detalle():
    if not session.get('admin_logueado'):
        return redirect(url_for('home'))

    desayunos = cargar_desayunos()
    desayuno = desayunos['CONDETALLE']

    if request.method == 'POST':
        nuevas_imagenes = desayuno['imagenes']
        for i in range(3):
            file_key = f'imagen_{i+1}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"detalle_{i+1}.jpg")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER_DETALLE'], filename))
                    nuevas_imagenes[i] = filename

        menu_file = request.files['imagen_menu']
        if menu_file and allowed_file(menu_file.filename):
            menu_filename = secure_filename("menu_detalle.jpg")
            menu_file.save(os.path.join(app.config['UPLOAD_FOLDER_DETALLE'], menu_filename))
            desayuno['imagen_menu'] = menu_filename

        desayuno['precio'] = float(request.form['precio'])
        guardar_desayunos(desayunos)
        flash('¡CON DETALLE actualizado!', 'success')
        return redirect(url_for('editar_detalle'))

    return render_template('editar_detalle.html', desayuno=desayuno)

if __name__ == '__main__':
    app.run(debug=True)