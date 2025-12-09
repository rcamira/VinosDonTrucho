# app.py
from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, flash
from bson import ObjectId
import utils.database as dbase
from models.product import Product
from bson.objectid import ObjectId
from datetime import datetime
from routes.product_routes import product_bp


dbase.dbConnection()
app = Flask(__name__)
app.secret_key = 'mysecretkey'


app.register_blueprint(product_bp)

# ---------- RUTAS EXISTENTES (las mantienes) ----------
@app.route('/')
def index_redirect():
    return redirect(url_for('products.product_list'))



# Manejo de errores
@app.errorhandler(404)
def notFound(error=None):
    if request.path.startswith('/api/'):
        message = {
            'message': 'No encontrado ' + request.url,
            'status': 404
        }

        return  jsonify(message), 404
    
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