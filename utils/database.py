from pymongo import MongoClient
import certifi
# Asegúrate de importar el error para que tu try/except funcione
from pymongo.errors import ServerSelectionTimeoutError 
#mongodb+srv://celeste:<db_password>@vinosdontrucho.qhaz43b.mongodb.net/
MONGO_URI = 'mongodb+srv://celeste:celeste@vinosdontrucho.qhaz43b.mongodb.net/'
ca = certifi.where()

def dbConnection():

    db = None
    try:

        client = MongoClient(MONGO_URI, tlsCAFile=ca, serverSelectionTimeoutMS=5000)
        

        client.admin.command('ping') 
        
     
        db = client["Don_TruchoDb"]
        print("--- Conexión a MongoDB Atlas Exitosa ---")
        return db
        
    except ServerSelectionTimeoutError as e:
        print(f"ERROR DE CONEXIÓN (TIMEOUT): {e}")
        # Retorna None si falla
        return None
    except Exception as e:
        print(f"ERROR DESCONOCIDO: {e}")
        return None