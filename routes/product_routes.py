from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from bson import ObjectId
from models.product import Product

# Crear Blueprint para productos
product_bp = Blueprint('products', __name__, url_prefix='/products')

@product_bp.route('/')
def list_products():
    """Listar todos los productos con filtros"""
    # Obtener parámetros de filtro
    nombre = request.args.get('nombre', '').strip()
    categoria = request.args.get('categoria', '').strip()
    min_precio = request.args.get('min_precio', '').strip()
    max_precio = request.args.get('max_precio', '').strip()
    
    # Obtener productos
    if nombre:
        products = Product.search_by_name(nombre)
    elif categoria and categoria != 'Todas':
        products = Product.filter_by_category(categoria)
    elif min_precio and max_precio:
        try:
            products = Product.filter_by_price_range(float(min_precio), float(max_precio))
        except ValueError:
            products = Product.get_all()
    else:
        products = Product.get_all()
    
    # Obtener categorías únicas para el filtro
    categories = Product.get_categories()
    
    return render_template('products/list.html', 
                         products=products,
                         categories=categories,
                         filtros={
                             'nombre': nombre,
                             'categoria': categoria,
                             'min_precio': min_precio,
                             'max_precio': max_precio
                         })

@product_bp.route('/new', methods=['GET'])
def new_product_form():
    """Mostrar formulario para nuevo producto"""
    categories = Product.get_categories()
    return render_template('products/new.html', categories=categories)

@product_bp.route('/new', methods=['POST'])
def create_product():
    """Crear nuevo producto"""
    try:
        # Obtener datos del formulario
        product_data = {
            "nombre": request.form.get('nombre', '').strip(),
            "descripcion": request.form.get('descripcion', '').strip(),
            "precio": request.form.get('precio', '0').strip(),
            "stock": request.form.get('stock', '0').strip(),
            "categoria": request.form.get('categoria', 'General').strip(),
            "imagen": request.form.get('imagen', '/static/images/default.jpg').strip()
        }
        
        # Validaciones
        if not product_data['nombre']:
            flash('El nombre del producto es requerido', 'danger')
            return redirect(url_for('products.new_product_form'))
        
        try:
            product_data['precio'] = float(product_data['precio'])
            product_data['stock'] = int(product_data['stock'])
            
            if product_data['precio'] < 0:
                flash('El precio no puede ser negativo', 'danger')
                return redirect(url_for('products.new_product_form'))
            
            if product_data['stock'] < 0:
                flash('El stock no puede ser negativo', 'danger')
                return redirect(url_for('products.new_product_form'))
                
        except ValueError:
            flash('Precio y stock deben ser números válidos', 'danger')
            return redirect(url_for('products.new_product_form'))
        
        # Crear producto
        product_id = Product.create(product_data)
        
        if product_id:
            flash('Producto creado exitosamente!', 'success')
            return redirect(url_for('products.view_product', product_id=product_id))
        else:
            flash('Error al crear el producto', 'danger')
            return redirect(url_for('products.new_product_form'))
            
    except Exception as e:
        print(f"Error al crear producto: {e}")
        flash('Error interno del servidor', 'danger')
        return redirect(url_for('products.new_product_form'))

@product_bp.route('/<product_id>')
def view_product(product_id):
    """Ver detalle de un producto"""
    try:
        product = Product.get_by_id(product_id)
        if product:
            return render_template('products/view.html', product=product)
        else:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('products.list_products'))
    except Exception as e:
        print(f"Error al ver producto: {e}")
        flash('ID de producto inválido', 'danger')
        return redirect(url_for('products.list_products'))

@product_bp.route('/<product_id>/edit', methods=['GET'])
def edit_product_form(product_id):
    """Mostrar formulario para editar producto"""
    try:
        product = Product.get_by_id(product_id)
        if product:
            categories = Product.get_categories()
            return render_template('products/edit.html', 
                                 product=product, 
                                 categories=categories)
        else:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('products.list_products'))
    except Exception as e:
        print(f"Error al cargar formulario de edición: {e}")
        flash('ID de producto inválido', 'danger')
        return redirect(url_for('products.list_products'))

@product_bp.route('/<product_id>/edit', methods=['POST'])
def update_product(product_id):
    """Actualizar producto existente"""
    try:
        # Obtener datos del formulario
        update_data = {
            "nombre": request.form.get('nombre', '').strip(),
            "descripcion": request.form.get('descripcion', '').strip(),
            "precio": request.form.get('precio', '0').strip(),
            "stock": request.form.get('stock', '0').strip(),
            "categoria": request.form.get('categoria', 'General').strip(),
            "imagen": request.form.get('imagen', '/static/images/default.jpg').strip()
        }
        
        # Validaciones
        if not update_data['nombre']:
            flash('El nombre del producto es requerido', 'danger')
            return redirect(url_for('products.edit_product_form', product_id=product_id))
        
        try:
            update_data['precio'] = float(update_data['precio'])
            update_data['stock'] = int(update_data['stock'])
            
            if update_data['precio'] < 0:
                flash('El precio no puede ser negativo', 'danger')
                return redirect(url_for('products.edit_product_form', product_id=product_id))
            
            if update_data['stock'] < 0:
                flash('El stock no puede ser negativo', 'danger')
                return redirect(url_for('products.edit_product_form', product_id=product_id))
                
        except ValueError:
            flash('Precio y stock deben ser números válidos', 'danger')
            return redirect(url_for('products.edit_product_form', product_id=product_id))
        
        # Actualizar producto
        result = Product.update(product_id, update_data)
        
        if result['modified_count'] > 0:
            flash('Producto actualizado exitosamente!', 'success')
        else:
            flash('No se realizaron cambios en el producto', 'info')
            
        return redirect(url_for('products.view_product', product_id=product_id))
            
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        flash('Error interno del servidor', 'danger')
        return redirect(url_for('products.edit_product_form', product_id=product_id))

@product_bp.route('/<product_id>/delete', methods=['GET'])
def delete_product_form(product_id):
    """Mostrar confirmación de eliminación"""
    try:
        product = Product.get_by_id(product_id)
        if product:
            return render_template('products/delete.html', product=product)
        else:
            flash('Producto no encontrado', 'danger')
            return redirect(url_for('products.list_products'))
    except Exception as e:
        print(f"Error al cargar confirmación de eliminación: {e}")
        flash('ID de producto inválido', 'danger')
        return redirect(url_for('products.list_products'))

@product_bp.route('/<product_id>/delete', methods=['POST'])
def delete_product(product_id):
    """Eliminar producto"""
    try:
        deleted_count = Product.delete(product_id)
        
        if deleted_count > 0:
            flash('Producto eliminado exitosamente!', 'success')
        else:
            flash('Producto no encontrado', 'danger')
            
        return redirect(url_for('products.list_products'))
            
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        flash('Error interno del servidor', 'danger')
        return redirect(url_for('products.list_products'))

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