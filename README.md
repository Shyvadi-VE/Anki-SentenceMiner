# Sentence Mining Anki

Herramienta en Python para Sentence Mining e integración con Anki.

---

## 📁 Estructura del Proyecto

```text
Sentence Minning Anki/
│
├── .venv/                 # Entorno virtual de Python
├── src/                   # Código fuente de la aplicación
│   ├── __init__.py        # Inicializador del paquete
│   └── main.py            # Lógica principal del punto de entrada
├── tests/                 # Pruebas unitarias
│   ├── __init__.py
│   └── test_main.py       # Prueba de verificación
├── .env                   # Variables de entorno locales (ignorado por Git)
├── .env.example           # Plantilla de variables de entorno
├── .gitignore             # Archivos y carpetas ignorados por Git
├── main.py                # Script ejecutable raíz
├── requirements.txt       # Dependencias de producción
└── README.md              # Documentación del proyecto
```

---

## 🚀 Requisitos Previos

- Python 3.10+ (Recomendado 3.13)
- Gestor de paquetes `pip`

---

## ⚙️ Configuración del Entorno

### 1. Activar el Entorno Virtual (`.venv`)

En Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

> **Nota para PowerShell:** Si recibes un error sobre directivas de ejecución, ejecuta antes:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

En Windows (CMD):
```cmd
.venv\Scripts\activate.bat
```

En Git Bash / Linux / macOS:
```bash
source .venv/Scripts/activate  # o bin/activate en Unix
```

### 2. Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### 3. Variables de Entorno

Copia el archivo `.env.example` a `.env` (si aún no existe) y ajusta tus variables:
```powershell
cp .env.example .env
```

---

## 🏃 Ejecución

Para iniciar el proyecto:
```powershell
python main.py
```

O como módulo:
```powershell
python -m src.main
```

---

## 🧪 Pruebas Unitarias

Para correr las pruebas:
```powershell
python -m unittest discover tests
```
