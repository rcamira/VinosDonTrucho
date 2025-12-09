# run.py - En la RAIZ del proyecto
"""
Script para ejecutar la aplicación de manera más profesional.
Útil para desarrollo y despliegue.
"""

import os
import sys
import webbrowser
from threading import Timer

# Asegurar que Python encuentre los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_setup():
    """Verificar que todo esté configurado correctamente"""
    print("🔍 Verificando configuración...")
    
    # 1. Verificar archivos necesarios
    required_files = [
        ('app.py', 'Aplicación Flask'),
        ('utils/database.py', 'Conexión a MongoDB'),
        ('models/product.py', 'Modelo de datos')
    ]
    
    all_ok = True
    for filename, description in required_files:
        if os.path.exists(filename):
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - No encontrado: {filename}")
            all_ok = False
    
    # 2. Verificar conexión a MongoDB
    try:
        import utils.database as dbase
        db = dbase.dbConnection()
        if db is not None:
            print("  ✅ Conexión a MongoDB")
            
            # Verificar colección 'products'
            if 'products' in db.list_collection_names():
                print("  ✅ Colección 'products' encontrada")
            else:
                print("  ⚠ Colección 'products' no existe (se creará automáticamente)")
        else:
            print("  ❌ No se pudo conectar a MongoDB")
            all_ok = False
            
    except Exception as e:
        print(f"  ❌ Error de conexión: {e}")
        all_ok = False
    
    return all_ok

def open_browser(port=4000):
    """Abrir navegador automáticamente"""
    url = f"http://localhost:{port}"
    print(f"\n🌐 Abriendo: {url}")
    webbrowser.open(url)

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🛒 GESTIÓN DE PRODUCTOS - FLASK + MONGODB")
    print("="*60)
    
    # Verificar configuración
    if not check_setup():
        print("\n❌ Problemas de configuración detectados.")
        print("   Por favor, corrige los errores antes de continuar.")
        sys.exit(1)
    
    # Configurar puerto
    port = 4000
    try:
        port = int(os.getenv('PORT', 4000))
    except:
        pass
    
    # Preguntar si abrir navegador
    print(f"\n⚙️  Puerto configurado: {port}")
    respuesta = input("¿Abrir navegador automáticamente? (s/n): ").strip().lower()
    
    if respuesta == 's':
        # Abrir después de 2 segundos
        Timer(2, lambda: open_browser(port)).start()
    
    # Importar y ejecutar la aplicación
    try:
        from app import app
        
        print("\n" + "="*60)
        print("🚀 INICIANDO SERVIDOR...")
        print("="*60)
        print("\n📞 URLs disponibles:")
        print(f"   • http://localhost:{port}/           - Página principal")
        print(f"   • http://localhost:{port}/products   - Lista de productos")
        print(f"   • http://localhost:{port}/products/new - Nuevo producto")
        print("\n📋 Comandos:")
        print("   Ctrl+C  - Detener servidor")
        print("="*60 + "\n")
        
        # Ejecutar Flask
        app.run(
            host='0.0.0.0',  # Accesible desde cualquier IP
            port=port,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"\n❌ Error al importar la aplicación: {e}")
        print("   Asegúrate de que app.py exista y no tenga errores.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()