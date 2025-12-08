# 🍷 VinosDonTrucho - Sistema de Gestión de Inventario

## 📋 Descripción del Proyecto
Aplicación web completa para la gestión de productos/inventario de una licorería desarrollada con **Flask**, **MongoDB Atlas** y **Bootstrap**. Permite realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre productos con búsqueda y filtros avanzados.

Este proyecto fue desarrollado como **Proyecto Final** para la materia de **Bases de Datos II**.

---

## ✨ Características Principales

### CRUD Completo
- ✅ **Crear productos** con todos sus atributos
- ✅ **Listar productos** en tarjetas con imágenes
- ✅ **Ver detalle** de cada producto
- ✅ **Editar productos** existentes
- ✅ **Eliminar productos** con confirmación previa

### Búsqueda y Filtros
- 🔍 **Búsqueda por nombre** (insensible a mayúsculas/minúsculas)
- 📁 **Filtro por categoría** (Ron, Vodka, Whisky, Cerveza, Otro)
- 💰 **Filtro por rango de precio** (mínimo y máximo)
- 🔄 **Combinación de filtros** (todos los filtros funcionan simultáneamente)
- 🧹 **Limpiar filtros** con un solo click

### Interfaz de Usuario
- 🎨 **Diseño responsive** con Bootstrap 5
- 🖼️ **Manejo de imágenes** mediante URLs externas
- 💬 **Mensajes flash** para feedback al usuario
- 🌙 **Tema oscuro** personalizado (fondo negro con detalles rojos)
- 📱 **Compatible con dispositivos móviles**

### Arquitectura
- 🗂️ **Vistas separadas** para cada operación CRUD
- 📦 **Código modular** organizado en carpetas
- 🔗 **Conexión a MongoDB Atlas** (base de datos en la nube)
- 🔒 **Validación de formularios**

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.10+ | Lenguaje principal |
| Flask | 2.3.3 | Framework web |
| MongoDB | 4.5.0 | Base de datos NoSQL |
| PyMongo | 4.5.0 | Driver de MongoDB |
| Bootstrap | 5.2.0 | Framework CSS |
| Font Awesome | 6.0.0 | Iconos |
| Jinja2 | Incluido en Flask | Motor de templates |

---

## 📁 Estructura del Proyecto

```
VinosDonTrucho/
│
├── app.py                      # Aplicación principal con todas las rutas
├── README.md                   # Este archivo
├── requerimentss.txt           # Dependencias del proyecto
│
├── models/
│   └── product.py              # Modelo de datos del producto
│
├── templates/
│   ├── base.html               # Plantilla base (layout)
│   ├── index.html              # Página principal (listado con filtros)
│   ├── product_form.html       # Formulario para crear/editar
│   ├── product_detail.html     # Vista detallada de un producto
│   └── confirm_delete.html     # Confirmación antes de eliminar
│
└── utils/
    └── database.py             # Configuración de conexión a MongoDB
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.10 o superior
- Cuenta en MongoDB Atlas (gratis)
- Git (opcional)

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/rcamira/vinosdontrucho.git
cd vinosdontrucho
```

### Paso 2: Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requerimentss.txt
```

### Paso 4: Configurar MongoDB Atlas

1. Crea una cuenta en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Crea un cluster gratuito (M0)
3. Configura un usuario de base de datos
4. Permite acceso desde cualquier IP (`0.0.0.0/0`) en Network Access
5. Obtén tu **connection string**

### Paso 5: Configurar Conexión a la Base de Datos

Abre `utils/database.py` y reemplaza la URI de conexión:

```python
MONGO_URI = 'tu_connection_string_aqui'
```

### Paso 6: Ejecutar la Aplicación
```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:4000**

---

## 📖 Guía de Uso

### Página Principal (Listado de Productos)
- **URL**: `/products` o `/`
- Muestra todos los productos en tarjetas
- Permite buscar y filtrar productos
- Botón para agregar nuevos productos

### Crear Nuevo Producto
- **URL**: `/products/new`
- Formulario con campos obligatorios:
  - Nombre
  - Descripción
  - Categoría (Ron, Vodka, Whisky, Cerveza, Otro)
  - Precio
  - Stock
  - URL de imagen

### Ver Detalle de Producto
- **URL**: `/products/<id>`
- Muestra toda la información del producto
- Incluye imagen ampliada
- Botones para editar o volver al listado

### Editar Producto
- **URL**: `/products/<id>/edit`
- Formulario precargado con los datos actuales
- Permite modificar cualquier campo

### Eliminar Producto
- **URL**: `/products/<id>/delete`
- Muestra confirmación antes de eliminar
- Botones para confirmar o cancelar

---

## 🔍 Funcionalidad de Búsqueda y Filtros

### Búsqueda por Nombre
Escribe cualquier parte del nombre del producto. La búsqueda es **insensible a mayúsculas/minúsculas**.

**Ejemplo**: Buscar "ron" encontrará "Ron Havana", "Ron Bacardi", etc.

### Filtro por Categoría
Selecciona una categoría del dropdown. Las categorías disponibles son:
- Ron
- Vodka
- Whisky
- Cerveza
- Otro

### Filtro por Precio
Define un rango de precio:
- **Precio Mínimo**: Muestra productos con precio mayor o igual
- **Precio Máximo**: Muestra productos con precio menor o igual
- Ambos campos son opcionales

### Combinación de Filtros
Puedes usar **todos los filtros simultáneamente**:

**Ejemplo**: Buscar "premium" + Categoría "Vodka" + Precio entre $30 y $50

### Limpiar Filtros
Presiona el botón **"Limpiar Filtros"** para resetear la búsqueda.

---

## 🗄️ Modelo de Datos

Cada producto en MongoDB tiene la siguiente estructura:

```javascript
{
  "_id": ObjectId("..."),
  "name": "Ron Havana Club 7 Años",
  "description": "Ron cubano añejado",
  "category": "Ron",
  "price": 45.50,
  "stock": 20,
  "image": "https://ejemplo.com/imagen.jpg"
}
```

---

## 🎨 Paleta de Colores

El diseño utiliza un tema oscuro personalizado:

- **Fondo principal**: Negro (`#000000`)
- **Tarjetas de productos**: Rojo oscuro (`#8B0000`)
- **Encabezados**: Rojo más oscuro (`#660000`)
- **Texto destacado**: Amarillo/Dorado (`text-warning`)
- **Texto principal**: Blanco (`#FFFFFF`)

---

## 🐛 Solución de Problemas Comunes

### Error: "No se puede conectar a MongoDB"
- Verifica que tu IP esté permitida en MongoDB Atlas (Network Access)
- Verifica que el connection string sea correcto
- Asegúrate de tener conexión a Internet

### Error: "ModuleNotFoundError: No module named 'flask'"
- Activa el entorno virtual: `venv\Scripts\activate`
- Instala las dependencias: `pip install -r requerimentss.txt`

### El servidor no inicia
- Verifica que el puerto 4000 no esté ocupado
- Cambia el puerto en `app.py`: `app.run(debug=True, port=5000)`

### Las imágenes no se cargan
- Verifica que las URLs de imágenes sean válidas y accesibles
- Usa URLs de servicios como Unsplash, Imgur, o similares

---

## 👥 Equipo de Desarrollo

Este proyecto fue desarrollado por:

- **[Tu Nombre]** - Frontend y diseño de interfaz
- **[Compañero 1]** - Backend y lógica de negocio
- **[Compañero 2]** - Base de datos y modelos

---

## 📝 Requisitos Cumplidos del Proyecto

### Requisitos Funcionales
- ✅ CRUD completo de productos
- ✅ Formulario de creación con todos los campos requeridos
- ✅ Listado de productos en tarjetas
- ✅ Actualización de productos
- ✅ Eliminación con confirmación previa

### Navegación y Vistas
- ✅ `/products` - Listado principal
- ✅ `/products/new` - Formulario de creación
- ✅ `/products/<id>` - Detalle del producto
- ✅ `/products/<id>/edit` - Formulario de edición
- ✅ `/products/<id>/delete` - Confirmación de eliminación

### Manejo de Imágenes
- ✅ Opción A: URLs externas de imágenes

### Filtros y Búsqueda
- ✅ Filtro por categoría
- ✅ Búsqueda por nombre
- ✅ Filtro por rango de precio
- ✅ Combinación de todos los filtros

### Requisitos Técnicos
- ✅ Flask como framework web
- ✅ MongoDB como base de datos
- ✅ Jinja2 para templates
- ✅ Código organizado en módulos

### Requisitos de Interfaz
- ✅ Bootstrap 5 para diseño
- ✅ Botones de CRUD visibles
- ✅ Diseño responsive
- ✅ Mensajes de feedback

---

## 📹 Video Demostrativo

**Pendiente**: Agregar enlace al video (máximo 3 minutos) mostrando:
- La aplicación funcionando
- Navegación por todas las vistas
- Uso de filtros y búsqueda
- Operaciones CRUD completas
- Explicación de la estructura del código

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos para la materia de Bases de Datos II.

---

## 🙏 Agradecimientos

- Profesor/a: [Nombre del profesor]
- Universidad: [Nombre de la universidad]
- Repositorio base: [Python-Flask-MongoDB](https://github.com/CodenautaJorge/Python-Flask-MongoDB)

---

**Fecha de entrega**: [Agregar fecha]
**Materia**: Bases de Datos II
**Semestre**: [semestre 2 - 2025]