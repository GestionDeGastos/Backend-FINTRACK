🚀 Descripción

Este proyecto implementa el backend del sistema de gestión de gastos personales.
Utiliza Python + FastAPI para el servidor, Supabase como base de datos y autenticación, y herramientas modernas para seguridad, estadísticas y visualización de datos.

⚙️ Requerimientos previos

Antes de iniciar asegúrate de tener instalado:

--Python 3.10+

--Git

--Visual Studio Code

--Una cuenta de Supabase

--Un archivo .env con tus claves de conexión (se configurará más adelante)

-------------🧩 Instalación paso a paso

1️⃣ Clonar el repositorio:

git clone https://github.com/GestionDeGastos/Backend-GestionGastos.git
cd Backend-GestionGastos


2️⃣ Crear el entorno virtual:

python -m venv venv


3️⃣ Activar el entorno virtual:

En VS Terminal PowerShell (Windows):

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate


En Linux / macOS:

source venv/bin/activate


4️⃣ Instalar las dependencias:

pip install -r requirements.txt


5️⃣ Ejecutar el servidor:

uvicorn main:app --reload


Abre en el navegador 👉 http://127.0.0.1:8000