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


@app.route('/products', methods=['GET'])
def products_list():
    products = db['products']
    
    # Obtener parámetros de búsqueda y filtros
    search_name = request.args.get('search', '').strip()
    filter_category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    
    # Construir query de MongoDB
    query = {}
    
    # Filtro por nombre (búsqueda)
    if search_name:
        query['name'] = {'$regex': search_name, '$options': 'i'}
    
    # Filtro por categoría
    if filter_category:
        query['category'] = filter_category
    
    # Filtro por rango de precio
    if min_price or max_price:
        query['price'] = {}
        if min_price:
            query['price']['$gte'] = float(min_price)
        if max_price:
            query['price']['$lte'] = float(max_price)
    
    # Ejecutar búsqueda con filtros
    productsReceived = products.find(query).sort('name')
    
    # Obtener categorías únicas para el select
    all_categories = products.distinct('category')
    
    return render_template('index.html', 
                         products=productsReceived, 
                         categories=all_categories,
                         search=search_name,
                         selected_category=filter_category,
                         min_price=min_price,
                         max_price=max_price)


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
        return render_template('product_detail.html', product=product)
    return notFound()


#Method delete Get
@app.route('/products/<string:product_id>/delete', methods=['GET'])
def confirm_delete_page(product_id):
    products = db['products']
    product = products.find_one({'_id': ObjectId(product_id)})
    if product:
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