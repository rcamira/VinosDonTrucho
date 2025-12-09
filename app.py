# app.py
from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, flash
from bson import ObjectId
import utils.database as dbase
from models.product import Product
from bson.objectid import ObjectId


db = dbase.dbConnection()
app = Flask(__name__)
app.secret_key = 'mysecretkey'

# ---------- RUTAS EXISTENTES (las mantienes) ----------
@app.route('/')
def index_redirect():
    return redirect(url_for('products_list'))


#@app.route('/products', methods=['GET'])
#def products_list():
 #   products = db['products']
  #  productsReceived = products.find().sort('name')
   # return render_template('index.html', products = productsReceived)
@app.route('/products', methods=['GET'])
def products_list():
    # Verificar conexión a la base de datos
    if db is None:
        flash('❌ Error: No hay conexión a MongoDB', 'error')
        return render_template('index.html', 
                             products=[], 
                             categories=[], 
                             current_category='', 
                             search_query='', 
                             min_price='', 
                             max_price='')
    
    try:
        products_col = db['products']
        
        # 1. OBTENER PARÁMETROS DE FILTRO DESDE LA URL
        category_filter = request.args.get('category', '')
        search_query = request.args.get('search', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        
        # 2. CONSTRUIR FILTRO DINÁMICO PARA MONGODB
        query_filter = {}
        
        # Filtro por categoría
        if category_filter:
            query_filter['category'] = category_filter
        
        # Búsqueda por nombre (búsqueda parcial, case-insensitive)
        if search_query:
            query_filter['name'] = {'$regex': search_query, '$options': 'i'}
        
        # Filtro por rango de precio
        if min_price or max_price:
            query_filter['price'] = {}
            if min_price:
                try:
                    query_filter['price']['$gte'] = float(min_price)  # Mayor o igual que
                except ValueError:
                    min_price = ''  # Si no es número válido, ignorar
            if max_price:
                try:
                    query_filter['price']['$lte'] = float(max_price)  # Menor o igual que
                except ValueError:
                    max_price = ''  # Si no es número válido, ignorar
        
        # 3. APLICAR FILTROS
        if query_filter:
            products_cursor = products_col.find(query_filter).sort('name')
        else:
            products_cursor = products_col.find().sort('name')
        
        # Convertir cursor a lista (importante para que funcione en plantilla)
        products_list = list(products_cursor)
        
        # 4. OBTENER CATEGORÍAS ÚNICAS PARA EL DROPDOWN
        try:
            categories = products_col.distinct('category')
        except:
            categories = []
        
        # 5. RENDERIZAR CON TODOS LOS DATOS
        return render_template('index.html', 
                             products=products_list,
                             categories=categories,
                             current_category=category_filter,
                             search_query=search_query,
                             min_price=min_price,
                             max_price=max_price)
    
    except Exception as e:
        print(f"❌ Error en products_list: {e}")
        flash(f'❌ Error al obtener productos: {str(e)}', 'error')
        return render_template('index.html', 
                             products=[], 
                             categories=[], 
                             current_category='', 
                             search_query='', 
                             min_price='', 
                             max_price='')
#Method Post
@app.route('/products', methods=['POST'])
def addProduct():

    products = db['products']

    name = request.form['name']
    description = request.form['description'] 
    price = request.form['price']
    stock = request.form['stock']             
    category = request.form['category']     
    image = request.form['image']

    if name and description and price and stock and category and image:

        product = Product(name, description, price, stock, category, image)    
        products.insert_one(product.toDBCollection())

        flash('Producto agregado correctamente')
        return redirect(url_for('products_list'))
    else:
        flash('¡Error! Faltan datos obligatorios.', 'error')
        return redirect(url_for('products_list'))


@app.route('/products/new', methods=['GET'])
def products_new_form():
    return render_template('product_form.html')


@app.route('/products/<string:product_id>', methods=['GET'])
def product_detail(product_id):
    products = db['products']
    product = products.find_one({'_id' : ObjectId(product_id)})
    if product:
        # Debes crear esta plantilla
        return render_template('product_detail.html', product=product)
    return notFound()



#Method delete Get
@app.route('/products/<string:product_id>/delete', methods=['GET'])
def confirm_delete_page(product_id):
    products = db['products']
    product = products.find_one({'_id': ObjectId(product_id)})
    if product:
        # Debes crear esta plantilla
        return render_template('confirm_delete.html', product=product) 
    return notFound()

#Method delete Post
@app.route('/products/<string:product_id>/delete', methods=['POST'])
def delete_product_action(product_id):
    products = db['products']
    products.delete_one({'_id' : ObjectId(product_id)})
    
    flash('Producto eliminado correctamente')
    return redirect(url_for('products_list'))



#Method Put
@app.route('/products/<string:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    products = db['products']

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock'] 
        category = request.form['category']
        image = request.form['image']

        if name and description and price and stock and category and image:
            updated_product = {
                'name' : name, 
                'description': description,
                'price' : float(price), 
                'stock' : int(stock),
                'category': category,
                'image': image
            }
            products.update_one({'_id' : ObjectId(product_id)}, {'$set' : updated_product})
            flash('Producto actualizado correctamente')
            return redirect(url_for('products_list'))
        
        else:
            flash('¡Error! Faltan datos obligatorios para la edición.', 'error')
            return redirect(url_for('products_list'))
    else:
        product_to_edit = products.find_one({'_id': ObjectId(product_id)})
        if product_to_edit:
            return render_template('product_form.html', product=product_to_edit, edit_mode=True)
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