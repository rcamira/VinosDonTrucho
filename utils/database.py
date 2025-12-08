from pymongo import MongoClient
import certifi
# Asegúrate de importar el error para que tu try/except funcione
from pymongo.errors import ServerSelectionTimeoutError 

MONGO_URI = 'mongodb+srv://brayansejas_adminDef:CqEGb9QVC4F2Vmg@cluster0.7c8la3d.mongodb.net/?appName=Cluster0'
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