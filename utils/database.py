from pymongo import MongoClient
import certifi

MONGO_URI = 'mongodb+srv://Amira:Amira@licoreria.n2cuqfc.mongodb.net/'
ca = certifi.where()

def dbConnection():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db = client["dbb_products_app"]
    except ConnectionError:
        print('Error de conexión con la bdd')
    return db
