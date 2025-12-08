from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, flash
import utils.database as dbase
from models.product import Product
from bson.objectid import ObjectId


db = dbase.dbConnection()
app = Flask(__name__)
app.secret_key = 'mysecretkey'

#Rutas de la aplicación
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


@app.errorhandler(404)
def notFound(error=None):
    message ={
        'message': 'No encontrado ' + request.url,
        'status': '404 Not Found'
    }
    response = jsonify(message)
    response.status_code = 404
    return response



if __name__ == '__main__':
    app.run(debug=True, port=4000)