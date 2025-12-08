from pymongo import MongoClient
import certifi

MONGO_URI = 'mongodb+srv://josecamachos1_db_user:Jcamacho5476@basededatos.s3rvs4n.mongodb.net/?appName=BaseDeDatos'
ca = certifi.where()

def dbConnection():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db = client["dbb_products_app"]
    except ConnectionError:
        print('Error de conexión con la bdd')
    return db
 