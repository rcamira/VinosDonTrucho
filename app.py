from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, flash
import utils.database as dbase
from models.product import Product

db = dbase.dbConnection()
app = Flask(__name__)

#Rutas de la aplicación
@app.route('/')
def home():
    products = db['products']

    name = request.args.get('name', '').strip()
    min_price_raw = request.args.get('min_price', '').strip()
    max_price_raw = request.args.get('max_price', '').strip()

    query = {}

    if name:
        query['name'] = {'$regex': name, '$options': 'i'}

    price_filter = {}
    if min_price_raw:
        try:
            min_price = float(min_price_raw)
            price_filter['$gte'] = min_price
        except ValueError:
            pass

    if max_price_raw:
        try:
            max_price = float(max_price_raw)
            price_filter['$lte'] = max_price
        except ValueError:
            pass

    if price_filter:
        query['price'] = price_filter

    productsReceived = products.find(query)
    return render_template('product_form.html', products=productsReceived)

#Method Post
@app.route('/products', methods=['POST'])
def addProduct():
    products = db['products']
    name = request.form['name']
    price = request.form['price']
    quantity = request.form['quantity']

    if name and price and quantity:
        product = Product(name, price, quantity)
        products.insert_one(product.toDBCollection())
        response = jsonify({
            'name' : name,
            'price' : price,
            'quantity' : quantity
        })
        return redirect(url_for('home'))
    else:
        return notFound()

#Method delete
@app.route('/delete/<string:product_name>')
def delete(product_name):
    products = db['products']
    products.delete_one({'name' : product_name})
    return redirect(url_for('home'))

#Method Put
@app.route('/edit/<string:product_name>', methods=['POST'])
def edit(product_name):
    products = db['products']
    name = request.form['name']
    price = request.form['price']
    quantity = request.form['quantity']

    if name and price and quantity:
        products.update_one({'name' : product_name}, {'$set' : {'name' : name, 'price' : price, 'quantity' : quantity}})
        response = jsonify({'message' : 'Producto ' + product_name + ' actualizado correctamente'})
        return redirect(url_for('home'))
    else:
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
    app.run(port=5000 ,debug=True)