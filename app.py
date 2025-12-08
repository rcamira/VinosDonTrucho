# app.py
from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, flash
from bson import ObjectId
import utils.database as dbase
from models.product import Product
from datetime import datetime

db = dbase.dbConnection()
app = Flask(__name__)
app.secret_key = 'clave_secreta_para_mensajes_flash'  # Necesario para flash()

# ---------- RUTAS EXISTENTES (las mantienes) ----------
@app.route('/')
def home():
    products = db['products']
    productsReceived = list(products.find())
    return render_template('index.html', products=productsReceived)

@app.route('/products', methods=['POST'])
def addProduct():
    products = db['products']
    name = request.form['name']
    price = request.form['price']
    quantity = request.form['quantity']

    if name and price and quantity:
        product = Product(name, price, quantity)
        products.insert_one(product.toDBCollection())
        flash('Producto creado exitosamente!', 'success')  # Mensaje flash
        return redirect(url_for('home'))
    else:
        return notFound()

@app.route('/delete/<string:product_name>')
def delete(product_name):
    products = db['products']
    products.delete_one({'name': product_name})
    flash('Producto eliminado!', 'info')
    return redirect(url_for('home'))

@app.route('/edit/<string:product_name>', methods=['POST'])
def edit(product_name):
    products = db['products']
    name = request.form['name']
    price = request.form['price']
    quantity = request.form['quantity']

    if name and price and quantity:
        products.update_one(
            {'name': product_name}, 
            {'$set': {
                'name': name, 
                'price': float(price), 
                'quantity': int(quantity),
                'updated_at': datetime.utcnow()
            }}
        )
        flash('Producto actualizado correctamente!', 'success')
        return redirect(url_for('home'))
    else:
        return notFound()

# ---------- NUEVAS RUTAS (según requisitos del proyecto) ----------

# Ruta para listar productos (vista separada)
@app.route('/products')
def list_products():
    """Muestra todos los productos en página separada"""
    products = db['products']
    
    # Manejar filtros
    categoria = request.args.get('categoria', '')
    nombre = request.args.get('nombre', '')
    min_precio = request.args.get('min_precio', '')
    max_precio = request.args.get('max_precio', '')
    
    query = {}
    
    if categoria and categoria != 'Todas':
        query['category'] = categoria
    
    if nombre:
        query['name'] = {'$regex': nombre, '$options': 'i'}
    
    if min_precio and max_precio:
        try:
            query['price'] = {
                '$gte': float(min_precio),
                '$lte': float(max_precio)
            }
        except:
            pass
    
    productsReceived = list(products.find(query))
    return render_template('products/list.html', products=productsReceived)

# Ruta para formulario de nuevo producto (vista separada)
@app.route('/products/new')
def new_product_form():
    """Muestra formulario para crear producto"""
    return render_template('products/new.html')

# Ruta para ver detalle de producto
@app.route('/products/<product_id>')
def view_product(product_id):
    """Muestra detalle de un producto específico"""
    try:
        products = db['products']
        product = products.find_one({'_id': ObjectId(product_id)})
        if product:
            return render_template('products/view.html', product=product)
        else:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('list_products'))
    except:
        flash('ID inválido', 'danger')
        return redirect(url_for('list_products'))

# Ruta para formulario de edición (vista separada)
@app.route('/products/<product_id>/edit')
def edit_product_form(product_id):
    """Muestra formulario para editar producto"""
    try:
        products = db['products']
        product = products.find_one({'_id': ObjectId(product_id)})
        if product:
            return render_template('products/edit.html', product=product)
        else:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('list_products'))
    except:
        flash('ID inválido', 'danger')
        return redirect(url_for('list_products'))

# Ruta para actualizar producto (nueva versión)
@app.route('/products/<product_id>/update', methods=['POST'])
def update_product(product_id):
    """Actualiza un producto existente"""
    try:
        products = db['products']
        
        # Obtener datos extendidos del formulario
        data = {
            'name': request.form.get('name', ''),
            'description': request.form.get('description', ''),
            'price': request.form.get('price', '0'),
            'quantity': request.form.get('quantity', '0'),
            'category': request.form.get('category', 'General'),
            'image': request.form.get('image', '/static/images/default.jpg'),
            'updated_at': datetime.utcnow()
        }
        
        # Convertir tipos
        try:
            data['price'] = float(data['price'])
            data['quantity'] = int(data['quantity'])
        except:
            flash('Precio y cantidad deben ser números válidos', 'danger')
            return redirect(url_for('edit_product_form', product_id=product_id))
        
        # Validar datos requeridos
        if not data['name'] or data['price'] < 0 or data['quantity'] < 0:
            flash('Datos inválidos', 'danger')
            return redirect(url_for('edit_product_form', product_id=product_id))
        
        # Actualizar en MongoDB
        result = products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': data}
        )
        
        if result.modified_count > 0:
            flash('Producto actualizado exitosamente!', 'success')
        else:
            flash('No se realizaron cambios', 'info')
            
        return redirect(url_for('view_product', product_id=product_id))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('list_products'))

# Ruta para confirmar eliminación (vista separada)
@app.route('/products/<product_id>/delete')
def delete_product_form(product_id):
    """Muestra confirmación para eliminar producto"""
    try:
        products = db['products']
        product = products.find_one({'_id': ObjectId(product_id)})
        if product:
            return render_template('products/delete.html', product=product)
        else:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('list_products'))
    except:
        flash('ID inválido', 'danger')
        return redirect(url_for('list_products'))

# Ruta para eliminar producto (nueva versión con confirmación)
@app.route('/products/<product_id>/delete', methods=['POST'])
def delete_product(product_id):
    """Elimina un producto con confirmación"""
    try:
        products = db['products']
        
        # Obtener nombre antes de eliminar para el mensaje
        product = products.find_one({'_id': ObjectId(product_id)})
        product_name = product['name'] if product else ''
        
        result = products.delete_one({'_id': ObjectId(product_id)})
        
        if result.deleted_count > 0:
            flash(f'Producto "{product_name}" eliminado exitosamente!', 'success')
        else:
            flash('Producto no encontrado', 'danger')
            
        return redirect(url_for('list_products'))
        
    except:
        flash('Error al eliminar producto', 'danger')
        return redirect(url_for('list_products'))

# Ruta para búsqueda avanzada
@app.route('/products/search')
def search_products():
    """Búsqueda con filtros combinados"""
    products = db['products']
    
    # Obtener todos los filtros
    filters = {}
    
    # Filtro por categoría
    category = request.args.get('category', '')
    if category and category != 'Todas':
        filters['category'] = category
    
    # Búsqueda por nombre
    name = request.args.get('name', '')
    if name:
        filters['name'] = {'$regex': name, '$options': 'i'}
    
    # Filtro por rango de precio
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    if min_price and max_price:
        try:
            filters['price'] = {
                '$gte': float(min_price),
                '$lte': float(max_price)
            }
        except:
            pass
    
    productsReceived = list(products.find(filters))
    return render_template('products/list.html', products=productsReceived)

# Manejo de errores
@app.errorhandler(404)
def notFound(error=None):
    if request.path.startswith('/api/'):
        message = {
            'message': 'No encontrado ' + request.url,
            'status': '404 Not Found'
        }
        response = jsonify(message)
        response.status_code = 404
        return response
    else:
        return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Punto de entrada
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Iniciando aplicación Flask + MongoDB")
    print(f"🌐 URL: http://localhost:4000")
    print("="*50)
    app.run(debug=True, port=4000)