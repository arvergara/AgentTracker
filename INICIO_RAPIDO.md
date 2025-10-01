# 🚀 Guía de Inicio Rápido - Comsulting Admin System

## ⚡ Instalación en 3 Pasos

### Paso 1: Instalar Dependencias
```bash
cd /mnt/user-data/outputs
pip install -r requirements.txt --break-system-packages
```

### Paso 2: Iniciar la Aplicación
```bash
python app.py
```

### Paso 3: Abrir en el Navegador
Abre tu navegador y ve a: **http://localhost:5000**

## 🎯 Primera Vez

Al abrir la aplicación por primera vez:

1. Ve a: http://localhost:5000/inicializar-datos
2. Esto creará datos de prueba (personas, clientes, horas, facturas)
3. Regresa al inicio y explora el Dashboard

## 📋 Funcionalidades Principales

### 1️⃣ Dashboard (http://localhost:5000/dashboard)
- Ver capacidad del equipo en tiempo real
- Alertas de personas sin registrar horas
- Calcular necesidad de contratación
- Top 5 clientes más rentables
- Rentabilidad por área
- Calculadora de pricing de proyectos

### 2️⃣ Personas (http://localhost:5000/personas)
- Ver equipo completo
- Agregar nuevas personas
- Ver reportes de productividad
- Recomendaciones de aumentos y bonos

### 3️⃣ Clientes (http://localhost:5000/clientes)
- Gestionar clientes permanentes y spot
- Analizar rentabilidad (6 meses o 1 año)
- Ver márgenes e ingresos

### 4️⃣ Registro de Horas (http://localhost:5000/horas)
- Registrar horas diarias
- Ver histórico de horas
- Filtrar por fecha y persona

## 🔥 Casos de Uso Rápidos

### ¿Tengo que contratar?
1. Dashboard → "Calculadora de Necesidad de Contratación"
2. Ingresa horas requeridas del nuevo cliente
3. Click "Calcular"
4. Te dice si necesitas contratar y qué cargo

### ¿Es rentable mi cliente?
1. Clientes → Buscar cliente
2. Click "6 Meses" o "1 Año"
3. Ver rentabilidad completa con márgenes

### ¿Cuánto cobrar por un proyecto?
1. Dashboard → "Calculadora de Pricing"
2. Ingresa horas por cargo
3. Ajusta margen deseado
4. Ver precio en UF y pesos

### ¿Merece aumento o bono?
1. Personas → Buscar persona
2. Click "📊 Productividad"
3. Ver ROI y recomendaciones automáticas

## 🛠️ Solución de Problemas

### Error: "No module named flask"
```bash
pip install -r requirements.txt --break-system-packages
```

### Puerto 5000 ocupado
Edita `app.py` línea final:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Base de datos corrupta
```bash
rm comsulting.db
python app.py
# Luego ve a: http://localhost:5000/inicializar-datos
```

## 📊 Datos de Ejemplo Incluidos

Al inicializar datos de prueba obtienes:
- ✅ 6 personas (Socios, Directores, Consultores)
- ✅ 4 clientes (permanentes y spot)
- ✅ 90 días de registros de horas
- ✅ Facturas de ejemplo
- ✅ Servicios y tareas por área

## 🎨 Personalización

### Cambiar horas efectivas mensuales
Edita en `app.py`:
```python
HORAS_EFECTIVAS_MES = 156  # Cambia este valor
```

### Cambiar porcentaje de impuestos
Edita en `app.py`:
```python
IMPUESTO = 0.27  # 27% por defecto
```

### Agregar nuevas áreas
Las áreas están en varios lugares del código. Busca:
- Formularios HTML (select options)
- Funciones de filtrado en JavaScript
- Modelos de datos en app.py

## 💾 Respaldo de Datos

Tu base de datos está en: `comsulting.db`

Para hacer respaldo:
```bash
cp comsulting.db comsulting_backup_$(date +%Y%m%d).db
```

## 📱 Acceso desde otros dispositivos

Para acceder desde otros dispositivos en la misma red:

1. Encuentra tu IP local:
```bash
# En Linux/Mac:
ifconfig | grep "inet "
# En Windows:
ipconfig
```

2. Otros dispositivos pueden acceder a:
```
http://TU_IP:5000
```

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Esta es una versión de desarrollo.

Para producción necesitas:
- Autenticación de usuarios
- Base de datos PostgreSQL/MySQL
- HTTPS
- Variables de entorno para configuración
- Validación de permisos por rol

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en la consola
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de tener Python 3.8 o superior

## 🎯 Próximos Pasos

Una vez que la aplicación esté funcionando:

1. ✅ Explora el Dashboard
2. ✅ Carga datos reales en Personas y Clientes
3. ✅ Comienza a registrar horas diarias
4. ✅ Revisa reportes de capacidad semanalmente
5. ✅ Analiza rentabilidad mensualmente
6. ✅ Usa pricing para nuevas propuestas

---

**¡Listo! Ya tienes tu sistema de administración funcionando** 🎉
