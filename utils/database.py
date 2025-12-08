from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Usar URI de .env o la predeterminada
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://Amira:Amira@licoreria.n2cuqfc.mongodb.net/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'dbb_products_app')
ca = certifi.where()

def dbConnection():
    """Conectar a MongoDB y retornar la base de datos"""
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db = client[DATABASE_NAME]
        
        # Probar la conexión
        client.admin.command('ping')
        print(f"✅ Conectado a MongoDB Atlas: {DATABASE_NAME}")
        
        return db
    except Exception as e:
        print(f'❌ Error de conexión con la base de datos: {e}')
        # Retornar None o manejar el error según necesites
        return None
