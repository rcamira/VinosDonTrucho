from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from bson import ObjectId
from datetime import datetime
from models.product import Product
import utils.database as dbase
db = dbase.dbConnection()


product_bp = Blueprint('products', __name__, url_prefix='/products')

@product_bp.route('/', methods=['GET'])
def product_list():
    """Listar todos los productos con filtros"""
    # Obtener parámetros de filtro
    products_col = db['products']
    category_filter = request.args.get('category', '')
    search_query = request.args.get('search', '') # <-- Tu template usa 'search'
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    
    
    query_filter = {}
    if category_filter:
        query_filter['category'] = category_filter
    if search_query:
        query_filter['name'] = {'$regex': search_query, '$options': 'i'}
    if min_price or max_price:
        query_filter['price'] = {}
        # Manejo de excepciones para precios (similar a tu código antiguo)
        try:
            if min_price: query_filter['price']['$gte'] = float(min_price)
            if max_price: query_filter['price']['$lte'] = float(max_price)
        except ValueError:
            flash('Error en formato de precio.', 'error')
            
    products_list = list(products_col.find(query_filter).sort('name'))
    categories = products_col.distinct('category') or []
    
    # 2. Renderizar el template INDEX.HTML que ya tienes
    return render_template('index.html', 
                           products=products_list,
                           categories=categories,
                           current_category=category_filter,
                           search_query=search_query,
                           min_price=min_price,
                           max_price=max_price)


@product_bp.route('/new', methods=['GET'])
def products_new_form():
    """Mostrar formulario para nuevo producto"""
    categories = db['products'].distinct('category') or []
    return render_template('product_form.html', categories=categories)


@product_bp.route('/', methods=['POST'])
def addproduct():
    """Crear nuevo producto"""
    try:
        # Obtener datos del formulario
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '0').strip()
        stock = request.form.get('stock', '0').strip()
        category = request.form.get('category', 'Otro').strip()
        image = request.form.get('image', 'url_defecto').strip()
        
        redirect_url_on_error = url_for('products.products_new_form')

        if not name or not price or not stock:
            flash('Faltan datos obligatorios.', 'error')
            return redirect(url_for('products.product_list'))
        
        # Manejo de la conversión de tipos (Aquí evitamos el ValueError)
        try:
            price_float = float(price)
            stock_int = int(stock)
        except ValueError:
            flash('ERROR: Precio y stock deben ser números válidos.', 'danger')
            return redirect(redirect_url_on_error)
            
        product = Product(
        name,         
        price_float,    
        stock_int,    
        description,   
        category,       
        image           
        )
        db['products'].insert_one(product.toDBCollection())

        flash('Producto agregado correctamente', 'success')
        return redirect(url_for('products.product_list'))
            
    except Exception as e:
        print(f"Error al crear producto: {e}")
        flash(f'Error interno del servidor: {e}', 'danger')
        return redirect(url_for('products.product_list'))



@product_bp.route('/<string:product_id>', methods=['GET'])
def product_detail(product_id): # <-- Renombrado para que coincida con tus templates
    """Ver detalle de un producto"""
    try:
        product = db['products'].find_one({'_id': ObjectId(product_id)})
        if product:
            # Renderiza el template product_detail.html que ya tienes
            return render_template('product_detail.html', product=product)
        else:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('products.product_list'))
    except:
        flash('ID inválido', 'danger')
        return redirect(url_for('products.product_list'))

@product_bp.route('/<string:product_id>/edit', methods=['GET'])
def edit_product(product_id): # <-- Renombrado para que coincida con tus templates
    """Mostrar formulario para editar producto"""
    try:
        product_to_edit = db['products'].find_one({'_id': ObjectId(product_id)})
        if product_to_edit:
             # Renderiza el template product_form.html que ya tienes, pasando 'product'
            return render_template('product_form.html', product=product_to_edit, edit_mode=True)
        else:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('products.product_list'))
    except:
        flash('ID inválido', 'danger')
        return redirect(url_for('products.product_list'))

@product_bp.route('/<product_id>/edit', methods=['POST'])
def update_product_action(product_id):
    return edit_product_post(product_id)
            
@product_bp.route('/<string:product_id>/edit', methods=['POST'])
def edit_product_post(product_id): # <-- Mantiene el nombre de ruta de tus templates
    # Lógica de POST de edición aquí
    products = db['products']
    
    # Obtener y validar datos... (Similar a addProduct)
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = float(request.form.get('price', '0').strip()) # Protegido por ValueError
        stock = int(request.form.get('stock', '0').strip())   # Protegido por ValueError
        category = request.form.get('category', '').strip()
        image = request.form.get('image', '').strip()
        
        updated_product = {
            'name' : name, 
            'description': description,
            'price' : price, 
            'stock' : stock,
            'category': category,
            'image': image,
            'updated_at': datetime.utcnow()
        }
        
        products.update_one({'_id' : ObjectId(product_id)}, {'$set' : updated_product})
        flash('Producto actualizado correctamente', 'success')
        return redirect(url_for('products.product_list'))
        
    except ValueError:
        flash('Error: Precio o stock deben ser números.', 'error')
        return redirect(url_for('products.edit_product', product_id=product_id))
    except Exception as e:
        flash(f'Error al actualizar: {str(e)}', 'error')
        return redirect(url_for('products.product_list'))     

@product_bp.route('/<string:product_id>/delete', methods=['GET'])
def confirm_delete_page(product_id): # <-- Renombrado para que coincida con tus templates
    """Muestra confirmación para eliminar producto"""
    try:
        product = db['products'].find_one({'_id': ObjectId(product_id)})
        if product:
            # Renderiza el template confirm_delete.html que ya tienes
            return render_template('confirm_delete.html', product=product) 
        else:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('products.product_list'))
    except:
        flash('ID inválido', 'danger')
        return redirect(url_for('products.product_list'))

@product_bp.route('/<string:product_id>/delete', methods=['POST'])
def delete_product_action(product_id): 
    """Eliminar producto"""
    try:
        result = db['products'].delete_one({'_id': ObjectId(product_id)})
        
        if result.deleted_count > 0:
            flash('Producto eliminado exitosamente!', 'success')
        else:
            flash('Producto no encontrado', 'danger')
            
        return redirect(url_for('products.product_list'))
            
    except Exception as e:
        flash('Error al eliminar producto', 'danger')
        return redirect(url_for('products.product_list'))

@product_bp.route('/stats')
def product_stats():
    """Estadísticas de productos (API)"""
    try:
        stats = Product.get_stats()
        return jsonify(stats)
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return jsonify({"error": "No se pudieron obtener estadísticas"}), 500

@product_bp.route('/api/all')
def api_all_products():
    """API para obtener todos los productos (JSON)"""
    try:
        products = Product.get_all()
        # Convertir ObjectId a string para JSON
        for product in products:
            product['_id'] = str(product['_id'])
            if 'created_at' in product:
                product['created_at'] = product['created_at'].isoformat()
            if 'updated_at' in product:
                product['updated_at'] = product['updated_at'].isoformat() if product['updated_at'] else None
        return jsonify(products)
    except Exception as e:
        print(f"Error en API: {e}")
        return jsonify({"error": str(e)}), 500