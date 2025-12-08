class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = float(price)
        self.quantity = int(quantity)

    def toDBCollection(self):
        return{
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity
        }