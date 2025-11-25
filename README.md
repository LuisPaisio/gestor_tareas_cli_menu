# 🧠 Gestor de Tareas CLI (Orientado a Objetos) + Login integrado

Gestor de tareas en consola desarrollado en Python, con sistema de usuarios, tienda, inventario y persistencia en JSON. Implementa un enfoque orientado a objetos con clases Usuario, GestorUsuarios, Tarea, GestorTareas, Inventario y Tienda. Permite crear, listar, editar, marcar como completas/incompletas y eliminar tareas desde la consola, con un sistema de gamificación que otorga recompensas y penalizaciones. En el futuro se planea integrar con Flask para una versión web.

---

## 🚀 Características
- Sistema de usuarios:
- Registro, inicio de sesión y eliminación de cuenta (GestorUsuarios)
- Estadísticas por usuario: vida, XP y coins

- Gestión de tareas (GestorTareas):
- Crear, listar, editar, marcar y eliminar tareas
- Tipos de tareas: hábitos, diarias y pendientes
- Recompensas por completar y penalizaciones por fallar

- Gamificación:
- Hábito positivo/negativo con impacto en stats
- Diarias que vencen cada día y aplican penalización si no se completan
- Pendientes con fecha de vencimiento
-  Mensajes claros y consistentes en colores (colorama)

- Inventario y Tienda:
- Comprar ítems con coins
- Vender ítems para recuperar parte del valor
- Persistencia en inventarios.json
- Catálogo definido en items.json

- Persistencia en JSON:
- Conversión objeto ↔ diccionario (to_dict() / from_dict())
- Archivos: usuarios, tareas, inventarios, recompensas

---

## 📂 Estructura del proyecto
```bash
gestor-tareas-cli/
│
├── menu_login.py          # Menú principal: login/registro/eliminar cuenta
├── usuario.py             # Clase Usuario: atributos y métodos
├── gestor_usuarios.py     # Clase GestorUsuarios: manejo de usuarios
├── menu_tareas.py         # Menú de tareas (CRUD, marcado, tienda)
├── gestor_tareas.py       # Clase GestorTareas: lógica de tareas
├── tareas.py              # Clase Tarea: definición y métodos
├── constantes_tareas.py   # Valores predeterminados de xp, coin, vida, etc
├── gestor_inventario.py   # Clase GestorInventario: manejo de inventarios
├── inventario.py          # Clase Inventario: manejo de ítems por usuario
├── menu_tienda.py         # Menú de Tienda
├── tienda.py              # Clase Tienda: catálogo, compra y venta
├── item.py                # Clase Item: definición de ítems de la tienda
├── recompensa.py          # Aún no implementado
├── json/
│   ├── usuarios.json      # Persistencia de usuarios
│   ├── tareas.json        # Persistencia de tareas
│   ├── inventarios.json   # Persistencia de inventarios
│   ├── items.json         # Catálogo de la tienda
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

## 🧪 Ejemplo de Uso
   ```bash
   === Menú Principal ===
   1. Iniciar sesión
   2. Registrarte
   3. Cancelar
   4. Eliminar cuenta

   === Menú Tareas ===
   1. Crear tarea
   2. Ver tareas
   3. Editar tarea
   4. Eliminar tarea
   5. Marcar tarea
   6. Perfil y Estadísticas
   7. Inventario
   8. Menú Tienda
   9. Salir

   === Menú Tienda ===
   1. Ver Catálogo
   2. Comprar Item
   3. Vender Item
   4. Volver al menú anterior
   ```

## 🗺️ Roadmap
- Integración con Flask para versión web
- Migración de persistencia a SQL
- Sistema de recompensas avanzado (niveles, logros, misiones)
- Inventario con ítems únicos y efectos en stats
- Tests unitarios y CI/CD

## 🤝 Contribución
¡Las contribuciones son bienvenidas!

- Haz un fork del repositorio.
- Crea una rama (git checkout -b feature/nueva-funcionalidad).
- Haz commit de tus cambios (git commit -m 'Agrega nueva funcionalidad').
- Haz push a la rama (git push origin feature/nueva-funcionalidad).
- Abre un Pull Request.

## 📄 Licencia
-Este proyecto está bajo la licencia MIT.
-Puedes usarlo, modificarlo y distribuirlo libremente, siempre mencionando al autor original.

## 📦 Requisitos
- Python 3.10 o superior
- Librerías listadas en `requirements.txt`

## 📌 Autor
- Luis — [Linkedin](https:www.linkedin.com/in/luis-paisio)
- Proyecto desarrollado como parte de su portfolio técnico.
