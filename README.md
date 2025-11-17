# 🧠 Gestor de Tareas CLI + login básico integrado

Gestor de tareas simple con menú integrado, desarrollado en Python.  
Permite crear, listar, editar, marcar como completas o incompletas y eliminar tareas desde la consola.  
Más adelante se planea integrar con **Flask** para una versión web.

## 🚀 Características
- Registrase, Iniciar Sesión o Eliminar Cuenta
- Crear nuevas tareas
- Listar tareas existentes
- Editar tareas por ID
- Marcar como completas o incompletas por ID
- Eliminar tareas por ID
- Persistencia en archivo JSON
- Mensajes en color usando `colorama`

## 📂 Estructura del proyecto
   ```bash
   gestor-tareas-cli/
   │
   ├── menu_login.py      # Archivo principal con menú login
   ├── login.py
   ├── usuarios.json
   ├── menu_tareas.py     # Archivo con menú de tareas
   ├── tareas.py          # Funciones para CRUD de tareas
   ├── tareas.json        # Archivo de persistencia
   ├── requirements.txt   # Dependencias
   └── README.md          # Documentación
   ```

## 🛠️ Instalación
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tuusuario/gestor-tareas-cli.git
   cd gestor-tareas-cli
   ```
2. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
4. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## 🧪 Uso
   ```bash
   python gestor.py
   ```

## 📦 Requisitos
- Python 3.10 o superior
- Librerías listadas en `requirements.txt`

## 📌 Autor
- Luis — [Linkedin](https:www.linkedin.com/in/luis-paisio)
- Proyecto desarrollado como parte de su portfolio técnico.
