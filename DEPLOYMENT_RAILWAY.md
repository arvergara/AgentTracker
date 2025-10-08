# 🚀 Guía de Deployment en Railway.app

## 📋 Preparación Completada ✅

Los siguientes archivos ya están listos:
- `requirements.txt` - Dependencias Python
- `Procfile` - Comando de inicio
- `railway.json` - Configuración Railway
- `.gitignore` - Archivos a ignorar
- Repositorio Git inicializado

---

## 🔧 Paso 1: Crear cuenta en Railway

1. Ve a https://railway.app
2. Click en **"Start a New Project"**
3. Inicia sesión con GitHub (o crea cuenta)

---

## 📤 Paso 2: Crear repositorio en GitHub

### Opción A: Desde la terminal (recomendado)

```bash
# Ya estás en el directorio AgentTracker
# Configura tu GitHub (si no lo has hecho)
gh auth login

# Crea el repositorio en GitHub
gh repo create AgentTracker --private --source=. --remote=origin --push
```

### Opción B: Manualmente en GitHub.com

1. Ve a https://github.com/new
2. Nombre: **AgentTracker**
3. Privado: ✅ (recomendado por info sensible)
4. NO inicialices con README (ya lo tenemos)
5. Click **"Create repository"**
6. Ejecuta en tu terminal:

```bash
cd "/Users/alfil/Library/CloudStorage/GoogleDrive-andres.vergara@maindset.cl/Mi unidad/Comsulting/AgentTracker"
git remote add origin https://github.com/TU_USUARIO/AgentTracker.git
git branch -M main
git push -u origin main
```

---

## 🚂 Paso 3: Deploy en Railway

1. **En Railway.app:**
   - Click **"New Project"**
   - Selecciona **"Deploy from GitHub repo"**
   - Autoriza acceso a GitHub
   - Selecciona el repo **AgentTracker**
   - Railway detectará automáticamente Python y Flask

2. **Espera el deploy** (2-3 minutos)
   - Railway instalará dependencias
   - Ejecutará gunicorn
   - Generará una URL temporal

3. **Verifica el deploy:**
   - Click en tu proyecto
   - Ve a **"Deployments"**
   - Verifica que esté ✅ **"Success"**
   - Click en **"View Logs"** si hay errores

---

## 🌐 Paso 4: Configurar dominio personalizado

### En Railway:

1. Ve a tu proyecto
2. Click en **"Settings"**
3. Sección **"Domains"**
4. Click **"Custom Domain"**
5. Ingresa: `agenttracker.alfil.io`
6. Railway te dará un CNAME (ej: `production-xyz.up.railway.app`)

### En Hostinger (Panel de Control DNS):

1. Inicia sesión en Hostinger
2. Ve a **Dominios** → **alfil.io**
3. Click en **"DNS/Name Servers"**
4. Agrega un nuevo registro:
   - **Type**: CNAME
   - **Name**: agenttracker
   - **Points to**: `production-xyz.up.railway.app` (el que te dio Railway)
   - **TTL**: 3600
5. Click **"Save"**

**⏰ Tiempo de propagación**: 5-30 minutos

---

## 🔐 Paso 5: Variables de entorno (IMPORTANTE)

En Railway, configura variables de entorno seguras:

1. Ve a **"Variables"**
2. Agrega:
   ```
   SECRET_KEY=TU_SECRET_KEY_MUY_SEGURA_AQUI
   FLASK_ENV=production
   ```

---

## ✅ Paso 6: Verificación

Una vez propagado el DNS, accede a:
- **https://agenttracker.alfil.io**

Deberías ver la página de login 🔐

**Credenciales:**
- Usuario: `admin`
- Contraseña: `comsulting2025`

---

## 🔄 Actualizaciones Futuras

Cada vez que hagas cambios:

```bash
cd "/Users/alfil/Library/CloudStorage/GoogleDrive-andres.vergara@maindset.cl/Mi unidad/Comsulting/AgentTracker"
git add .
git commit -m "Descripción del cambio"
git push
```

Railway detectará el push y redesplegará automáticamente ⚡

---

## 💰 Costos

- **Plan Hobby (Recomendado)**: $5/mes
  - 500 horas de ejecución
  - 8GB RAM
  - SSL/HTTPS incluido
  - Suficiente para AgentTracker

- **Plan Developer (Free)**: 
  - $5 crédito inicial
  - Luego $5/mes

---

## 🆘 Troubleshooting

### Error: "Application failed to start"
- Verifica logs en Railway
- Asegúrate de que requirements.txt está correcto
- Verifica que Procfile existe

### Error: "Database locked"
- Railway usa sistema de archivos efímero
- Considera migrar a PostgreSQL (gratis en Railway)
- O usa railway volumes para persistir SQLite

### Dominio no funciona
- Verifica CNAME en Hostinger
- Espera hasta 1 hora para propagación DNS
- Usa https://dnschecker.org para verificar

---

## 📊 Migrando a PostgreSQL (Recomendado)

Para producción, es mejor usar PostgreSQL:

1. En Railway, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway creará la base de datos
3. Modifica `app.py`:
   ```python
   import os
   
   # Cambiar de SQLite a PostgreSQL
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///comsulting.db')
   ```
4. Agrega a requirements.txt:
   ```
   psycopg2-binary==2.9.9
   ```
5. Push cambios
6. Railway automáticamente conectará la DB

---

## 📧 Soporte

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Hostinger Support: https://www.hostinger.com/contact

---

✨ **¡Listo! AgentTracker estará online 24/7 en agenttracker.alfil.io**
