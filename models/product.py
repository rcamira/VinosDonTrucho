# models/product.py
from datetime import datetime

class Product:
    def __init__(self, name, price, quantity, description="", category="General", image=""):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.description = description
        self.category = category
        self.image = image or "/static/images/default.jpg"
        self.created_at = datetime.utcnow()
    
    def toDBCollection(self):
        """Convertir a diccionario para MongoDB"""
        return {
            "name": self.name,
            "price": float(self.price),
            "quantity": int(self.quantity),
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
            quantity=data.get('quantity', 0),
            description=data.get('description', ''),
            category=data.get('category', 'General'),
            image=data.get('image', '/static/images/default.jpg')
        )
        return product
