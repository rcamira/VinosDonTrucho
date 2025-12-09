# models/product.py
from datetime import datetime
from bson import ObjectId
import utils.database as dbase


try:
    db = dbase.get_db()
except:
    # Si la conexión falla aquí, se debe inicializar en app.py primero.
    # Usaremos una variable temporal, aunque lo ideal es que get_db() funcione.
    db = None


class Product:
    def __init__(self, name, price, stock, description="", category="General", image=""):
        self.name = name
        self.price = price
        self.stock = stock
        self.description = description
        self.category = category
        self.image = image or "/static/images/default.jpg"
        self.created_at = datetime.utcnow()
        self.updated_at = None
    
    def toDBCollection(self):
        """Convertir a diccionario para MongoDB"""
        return {
            "name": self.name,
            "price": float(self.price),
            "stock": int(self.stock),
            "description": self.description,
            "category": self.category,
            "image": self.image,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Crear objeto Product desde diccionario de MongoDB"""
        product = Product(
            name=data.get('name', ''),
            price=data.get('price', 0),
            stock=data.get('stock', 0),
            description=data.get('description', ''),
            category=data.get('category', 'General'),
            image=data.get('image', '/static/images/default.jpg')
        )
        return product
    
    @staticmethod
    def get_all():
        """Obtiene todos los productos de la colección."""
        global db
        if db is None:
            db = dbase.get_db()

        # Retorna un cursor convertido a lista (diccionarios de Python)
        return list(db['products'].find({}))

    @staticmethod
    def get_stats():
        """Calcula y retorna estadísticas básicas."""
        global db
        if db is None:
            db = dbase.get_db()
            
        products_col = db['products']
        
        # 1. Total de productos
        total_products = products_col.count_documents({})
        
        # 2. Stock total (suma del campo 'stock')
        stock_aggregation = list(products_col.aggregate([
            {'$group': {'_id': None, 'total_stock': {'$sum': '$stock'}}}
        ]))
        total_stock = stock_aggregation[0]['total_stock'] if stock_aggregation else 0
        
        # 3. Categoría más popular
        category_counts = list(products_col.aggregate([
            {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 1}
        ]))

        return {
            "total_products": total_products,
            "total_stock": total_stock,
            "most_popular_category": category_counts[0]['_id'] if category_counts else "N/A"
        }
