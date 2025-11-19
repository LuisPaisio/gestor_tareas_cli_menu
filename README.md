# 🧠 Gestor de Tareas CLI (Orientado a Objetos) + Login integrado

Gestor de tareas en consola desarrollado en **Python**, con sistema de usuarios y persistencia en JSON.  
Implementa un enfoque **orientado a objetos** con clases `Usuario`, `GestorUsuarios`, `Tarea` y `GestorTareas`.  
Permite crear, listar, editar, marcar como completas/incompletas y eliminar tareas desde la consola.  
En el futuro se planea integrar con **Flask** para una versión web.

---

## 🚀 Características
- Sistema de usuarios:
  - Registrarse, iniciar sesión y eliminar cuenta (`GestorUsuarios`)
- Gestión de tareas por usuario (`GestorTareas`)
- Tareas como objetos (`Tarea`) con atributos y métodos
- Crear nuevas tareas
- Listar tareas existentes con estado y vencimiento
- Editar tareas por ID visual
- Marcar como completas o incompletas
- Eliminar tareas
- Persistencia en archivo JSON con conversión objeto ↔ diccionario (`to_dict()` / `from_dict()`)
- Mensajes en color usando `colorama`

---

## 📂 Estructura del proyecto
```bash
gestor-tareas-cli/
│
├── menu_login.py          # Menú principal: login/registro/eliminar cuenta
├── menu_tareas.py         # Menú de tareas (CRUD y marcado)
├── gestor_usuarios.py     # Clase GestorUsuarios: manejo de usuarios
├── usuario.py             # Clase Usuario: atributos y métodos del usuario
├── gestor_tareas.py       # Clase GestorTareas: lógica de tareas
├── tareas.py              # Clase Tarea: definición y métodos
├── json/
│   ├── usuarios.json      # Persistencia de usuarios
│   ├── tareas.json        # Persistencia de tareas
│   └── recompensas.json   # Persistencia de recompensas (aún no implementado)
├── requirements.txt       # Dependencias
└── README.md              # Documentación

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
   python menu_login.py
   ```

## 📦 Requisitos
- Python 3.10 o superior
- Librerías listadas en `requirements.txt`

## 📌 Autor
- Luis — [Linkedin](https:www.linkedin.com/in/luis-paisio)
- Proyecto desarrollado como parte de su portfolio técnico.
