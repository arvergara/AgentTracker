from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, extract
from decimal import Decimal
from functools import wraps
import requests
import os
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comsulting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'comsulting-secret-key-2025-muy-segura-cambiar-en-produccion'

db = SQLAlchemy(app)

# ============= AUTENTICACIÓN =============

# Credenciales (en producción, usar base de datos con hash)
USERS = {
    'admin': hashlib.sha256('comsulting2025'.encode()).hexdigest(),
    'blanca': hashlib.sha256('bulnes2025'.encode()).hexdigest(),
    'macarena': hashlib.sha256('puiggredon2025'.encode()).hexdigest(),
}

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Constantes
HORAS_EFECTIVAS_MES = 156
IMPUESTO = 0.27  # 27% de impuestos en Chile

# ============= MODELOS DE BASE DE DATOS =============

class Persona(db.Model):
    __tablename__ = 'personas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cargo = db.Column(db.String(50))  # Socio, Director, Consultor, etc.
    tipo_jornada = db.Column(db.String(20), default='full-time')  # full-time, media-jornada
    area = db.Column(db.String(50))  # Externas, Internas, Asuntos Públicos, Redes sociales, Diseño
    costo_hora = db.Column(db.Float, nullable=False)  # Costo por hora en UF
    sueldo_mensual = db.Column(db.Float)  # Sueldo en UF
    activo = db.Column(db.Boolean, default=True)
    reporte_directo_id = db.Column(db.Integer, db.ForeignKey('personas.id'))
    
    horas = db.relationship('RegistroHora', back_populates='persona', lazy='dynamic')
    
    def __repr__(self):
        return f'<Persona {self.nombre}>'

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20))  # permanente, spot
    area = db.Column(db.String(50))  # Externas, Internas, etc.
    activo = db.Column(db.Boolean, default=True)
    fecha_inicio = db.Column(db.Date)
    
    horas = db.relationship('RegistroHora', back_populates='cliente', lazy='dynamic')
    facturas = db.relationship('Factura', back_populates='cliente', lazy='dynamic')
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'

class Servicio(db.Model):
    __tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(50))

    def __repr__(self):
        return f'<Servicio {self.nombre}>'

# Tabla de asociación Cliente-Servicio (muchos a muchos)
class ClienteServicio(db.Model):
    __tablename__ = 'cliente_servicio'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True)

    cliente = db.relationship('Cliente', backref='servicios_asociados')
    servicio = db.relationship('Servicio', backref='clientes_asociados')

    def __repr__(self):
        return f'<ClienteServicio {self.cliente.nombre} - {self.servicio.nombre}>'

class Tarea(db.Model):
    __tablename__ = 'tareas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'))

    servicio = db.relationship('Servicio', backref='tareas')

    def __repr__(self):
        return f'<Tarea {self.nombre}>'

class Proyecto(db.Model):
    __tablename__ = 'proyectos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    codigo = db.Column(db.String(50), unique=True)  # Ej: "BN-CAM-2025"
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'))
    tipo = db.Column(db.String(20))  # permanente, spot, interno
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    presupuesto_uf = db.Column(db.Float)
    estado = db.Column(db.String(20), default='activo')  # activo, pausado, cerrado, facturado
    descripcion = db.Column(db.Text)
    margen_objetivo = db.Column(db.Float)  # Margen deseado en %

    cliente = db.relationship('Cliente', backref='proyectos')
    servicio = db.relationship('Servicio', backref='proyectos')
    horas = db.relationship('RegistroHora', back_populates='proyecto', lazy='dynamic')
    facturas = db.relationship('Factura', back_populates='proyecto', lazy='dynamic')
    asignaciones = db.relationship('AsignacionProyecto', back_populates='proyecto', lazy='dynamic')

    def __repr__(self):
        return f'<Proyecto {self.codigo} - {self.nombre}>'

class AsignacionProyecto(db.Model):
    __tablename__ = 'asignaciones_proyecto'
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=False)
    rol_proyecto = db.Column(db.String(50))  # lider, colaborador, soporte
    horas_estimadas = db.Column(db.Float)
    costo_hora_proyecto = db.Column(db.Float)  # Override del costo estándar si es necesario
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True)

    persona = db.relationship('Persona', backref='asignaciones_proyecto')
    proyecto = db.relationship('Proyecto', back_populates='asignaciones')

    def __repr__(self):
        return f'<AsignacionProyecto {self.persona.nombre if self.persona else "?"} en {self.proyecto.codigo if self.proyecto else "?"}>'

class RegistroHora(db.Model):
    __tablename__ = 'registro_horas'
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'))  # NUEVO: Relación con proyecto
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'))
    tarea_id = db.Column(db.Integer, db.ForeignKey('tareas.id'))
    fecha = db.Column(db.Date, nullable=False)
    horas = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)

    persona = db.relationship('Persona', back_populates='horas')
    cliente = db.relationship('Cliente', back_populates='horas')
    proyecto = db.relationship('Proyecto', back_populates='horas')
    servicio = db.relationship('Servicio')
    tarea = db.relationship('Tarea')

    def __repr__(self):
        return f'<RegistroHora {self.persona.nombre} - {self.horas}h>'

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'))  # NUEVO: Relación con proyecto
    numero = db.Column(db.String(50))
    fecha = db.Column(db.Date, nullable=False)
    monto_uf = db.Column(db.Float, nullable=False)
    monto_pesos = db.Column(db.Float)
    pagada = db.Column(db.Boolean, default=False)

    cliente = db.relationship('Cliente', back_populates='facturas')
    proyecto = db.relationship('Proyecto', back_populates='facturas')  # NUEVO

    def __repr__(self):
        return f'<Factura {self.numero} - {self.monto_uf} UF>'

class ValorUF(db.Model):
    __tablename__ = 'valor_uf'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, unique=True)
    valor = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<ValorUF {self.fecha} - ${self.valor}>'

# ============= FUNCIONES AUXILIARES =============

def obtener_uf_actual():
    """Obtiene el valor actual de la UF desde la API del Banco Central o base de datos"""
    try:
        # Primero intentar obtener de la base de datos (valor más reciente)
        uf_reciente = ValorUF.query.order_by(ValorUF.fecha.desc()).first()
        if uf_reciente and uf_reciente.fecha >= datetime.now().date() - timedelta(days=1):
            return uf_reciente.valor
        
        # Si no hay valor reciente, usar un valor por defecto actualizado
        # En producción, aquí se haría una llamada a la API del Banco Central
        valor_uf = 37500  # Valor aproximado en pesos chilenos
        
        # Guardar en la base de datos
        nueva_uf = ValorUF(fecha=datetime.now().date(), valor=valor_uf)
        db.session.add(nueva_uf)
        db.session.commit()
        
        return valor_uf
    except Exception as e:
        print(f"Error obteniendo UF: {e}")
        return 37500  # Valor por defecto

def calcular_capacidad_equipo(periodo_meses=1):
    """Calcula la capacidad disponible del equipo"""
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=30 * periodo_meses)
    
    personas = Persona.query.filter_by(activo=True).all()
    resultados = []
    
    for persona in personas:
        # Calcular horas trabajadas en el período
        horas_trabajadas = db.session.query(func.sum(RegistroHora.horas))\
            .filter(RegistroHora.persona_id == persona.id)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0
        
        # Calcular horas disponibles según tipo de jornada
        if persona.tipo_jornada == 'full-time':
            horas_disponibles = HORAS_EFECTIVAS_MES * periodo_meses
        else:
            horas_disponibles = (HORAS_EFECTIVAS_MES / 2) * periodo_meses
        
        # Calcular porcentaje de utilización
        porcentaje_utilizacion = (horas_trabajadas / horas_disponibles * 100) if horas_disponibles > 0 else 0
        capacidad_disponible = horas_disponibles - horas_trabajadas
        
        resultados.append({
            'persona': persona.nombre,
            'cargo': persona.cargo,
            'area': persona.area,
            'horas_trabajadas': round(horas_trabajadas, 2),
            'horas_disponibles': round(horas_disponibles, 2),
            'capacidad_disponible': round(capacidad_disponible, 2),
            'porcentaje_utilizacion': round(porcentaje_utilizacion, 2),
            'estado': 'sobrecargado' if porcentaje_utilizacion > 100 else 'disponible' if porcentaje_utilizacion < 80 else 'optimo'
        })
    
    return resultados

def personas_sin_horas_recientes():
    """Identifica personas que no han registrado horas en los últimos 2 días"""
    fecha_limite = datetime.now().date() - timedelta(days=2)
    
    personas_activas = Persona.query.filter_by(activo=True).all()
    sin_registro = []
    
    for persona in personas_activas:
        ultima_hora = RegistroHora.query\
            .filter(RegistroHora.persona_id == persona.id)\
            .filter(RegistroHora.fecha >= fecha_limite)\
            .first()
        
        if not ultima_hora:
            reporte_directo = Persona.query.get(persona.reporte_directo_id) if persona.reporte_directo_id else None
            sin_registro.append({
                'persona': persona.nombre,
                'email': persona.email,
                'reporte_directo': reporte_directo.nombre if reporte_directo else 'N/A',
                'email_reporte': reporte_directo.email if reporte_directo else None
            })
    
    return sin_registro

def calcular_necesidad_contratacion(horas_socio, horas_director, horas_consultor, area):
    """Determina si se necesita contratar nueva persona"""
    capacidad = calcular_capacidad_equipo(periodo_meses=1)
    
    # Filtrar por área si se especifica
    if area:
        capacidad = [c for c in capacidad if c['area'] == area]
    
    # Separar por cargo
    socios = [c for c in capacidad if 'Socio' in c['cargo']]
    directores = [c for c in capacidad if 'Director' in c['cargo']]
    consultores = [c for c in capacidad if 'Consultor' in c['cargo']]
    
    recomendacion = {
        'contratar': False,
        'cargo': None,
        'razon': '',
        'capacidad_actual': {}
    }
    
    # Verificar socios
    capacidad_socios = sum([s['capacidad_disponible'] for s in socios])
    if horas_socio > capacidad_socios:
        recomendacion['contratar'] = True
        recomendacion['cargo'] = 'Socio'
        recomendacion['razon'] = f'Se requieren {horas_socio}h de Socio, pero solo hay {round(capacidad_socios, 2)}h disponibles'
    
    # Verificar directores
    capacidad_directores = sum([d['capacidad_disponible'] for d in directores])
    if horas_director > capacidad_directores:
        if not recomendacion['contratar']:
            recomendacion['contratar'] = True
            recomendacion['cargo'] = 'Director'
            recomendacion['razon'] = f'Se requieren {horas_director}h de Director, pero solo hay {round(capacidad_directores, 2)}h disponibles'
    
    # Verificar consultores
    capacidad_consultores = sum([c['capacidad_disponible'] for c in consultores])
    if horas_consultor > capacidad_consultores:
        if not recomendacion['contratar']:
            recomendacion['contratar'] = True
            recomendacion['cargo'] = 'Consultor'
            recomendacion['razon'] = f'Se requieren {horas_consultor}h de Consultor, pero solo hay {round(capacidad_consultores, 2)}h disponibles'
    
    recomendacion['capacidad_actual'] = {
        'socios': round(capacidad_socios, 2),
        'directores': round(capacidad_directores, 2),
        'consultores': round(capacidad_consultores, 2)
    }
    
    return recomendacion

def calcular_rentabilidad_cliente(cliente_id, periodo_meses=12):
    """Calcula la rentabilidad de un cliente"""
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=30 * periodo_meses)
    
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return None
    
    # Calcular costos (horas trabajadas * costo por hora)
    horas_query = db.session.query(
        func.sum(RegistroHora.horas * Persona.costo_hora)
    ).join(Persona)\
        .filter(RegistroHora.cliente_id == cliente_id)\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)
    
    costos_totales = horas_query.scalar() or 0
    
    # Calcular ingresos (facturas)
    ingresos_query = db.session.query(func.sum(Factura.monto_uf))\
        .filter(Factura.cliente_id == cliente_id)\
        .filter(Factura.fecha >= fecha_inicio)\
        .filter(Factura.fecha <= fecha_fin)
    
    ingresos_totales_uf = ingresos_query.scalar() or 0
    
    # Obtener valor UF
    valor_uf = obtener_uf_actual()
    ingresos_totales_pesos = ingresos_totales_uf * valor_uf
    costos_totales_pesos = costos_totales * valor_uf
    
    # Calcular utilidad y margen
    utilidad_bruta = ingresos_totales_uf - costos_totales
    margen = (utilidad_bruta / ingresos_totales_uf * 100) if ingresos_totales_uf > 0 else 0
    
    # Calcular utilidad después de impuestos
    utilidad_despues_impuestos = utilidad_bruta * (1 - IMPUESTO)
    
    return {
        'cliente': cliente.nombre,
        'periodo_meses': periodo_meses,
        'ingresos_uf': round(ingresos_totales_uf, 2),
        'ingresos_pesos': round(ingresos_totales_pesos, 0),
        'costos_uf': round(costos_totales, 2),
        'costos_pesos': round(costos_totales_pesos, 0),
        'utilidad_bruta_uf': round(utilidad_bruta, 2),
        'utilidad_bruta_pesos': round(utilidad_bruta * valor_uf, 0),
        'utilidad_neta_uf': round(utilidad_despues_impuestos, 2),
        'utilidad_neta_pesos': round(utilidad_despues_impuestos * valor_uf, 0),
        'margen': round(margen, 2),
        'valor_uf': valor_uf
    }

def ranking_clientes_rentables(year=None, top=10):
    """Genera ranking de clientes más rentables"""
    if not year:
        year = datetime.now().year
    
    clientes = Cliente.query.filter_by(activo=True).all()
    rentabilidades = []
    
    for cliente in clientes:
        rent = calcular_rentabilidad_cliente(cliente.id, periodo_meses=12)
        if rent and rent['ingresos_uf'] > 0:
            rentabilidades.append(rent)
    
    # Ordenar por utilidad neta
    rentabilidades.sort(key=lambda x: x['utilidad_neta_uf'], reverse=True)
    
    return rentabilidades[:top]

def rentabilidad_por_area(year=None):
    """Calcula rentabilidad por área de Comsulting"""
    if not year:
        year = datetime.now().year
    
    areas = ['Externas', 'Internas', 'Asuntos Públicos', 'Redes sociales', 'Diseño']
    resultados = []
    
    for area in areas:
        clientes_area = Cliente.query.filter_by(area=area, activo=True).all()
        
        ingresos_total = 0
        costos_total = 0
        
        for cliente in clientes_area:
            rent = calcular_rentabilidad_cliente(cliente.id, periodo_meses=12)
            if rent:
                ingresos_total += rent['ingresos_uf']
                costos_total += rent['costos_uf']
        
        utilidad = ingresos_total - costos_total
        margen = (utilidad / ingresos_total * 100) if ingresos_total > 0 else 0
        
        resultados.append({
            'area': area,
            'ingresos_uf': round(ingresos_total, 2),
            'costos_uf': round(costos_total, 2),
            'utilidad_uf': round(utilidad, 2),
            'margen': round(margen, 2)
        })
    
    return sorted(resultados, key=lambda x: x['utilidad_uf'], reverse=True)

def calcular_precio_proyecto(horas_por_cargo, margen_deseado=12.5):
    """
    Calcula el precio a cobrar por un proyecto
    horas_por_cargo: dict con formato {'Socio': horas, 'Director': horas, 'Consultor': horas}
    margen_deseado: margen antes de impuestos en porcentaje
    """
    costo_total = 0
    detalle = []
    
    for cargo, horas in horas_por_cargo.items():
        # Buscar costo promedio por cargo
        personas = Persona.query.filter(
            Persona.cargo.like(f'%{cargo}%'),
            Persona.activo == True
        ).all()
        
        if personas:
            costo_promedio = sum([p.costo_hora for p in personas]) / len(personas)
            costo = horas * costo_promedio
            costo_total += costo
            
            detalle.append({
                'cargo': cargo,
                'horas': horas,
                'costo_hora_uf': round(costo_promedio, 2),
                'costo_total_uf': round(costo, 2)
            })
    
    # Calcular precio con margen deseado (antes de impuestos)
    precio_sin_impuestos = costo_total / (1 - (margen_deseado / 100))
    
    # Calcular utilidad
    utilidad_bruta = precio_sin_impuestos - costo_total
    utilidad_neta = utilidad_bruta * (1 - IMPUESTO)
    
    # Margen después de impuestos
    margen_neto = (utilidad_neta / precio_sin_impuestos * 100) if precio_sin_impuestos > 0 else 0
    
    valor_uf = obtener_uf_actual()
    
    return {
        'costo_total_uf': round(costo_total, 2),
        'costo_total_pesos': round(costo_total * valor_uf, 0),
        'precio_cobrar_uf': round(precio_sin_impuestos, 2),
        'precio_cobrar_pesos': round(precio_sin_impuestos * valor_uf, 0),
        'utilidad_bruta_uf': round(utilidad_bruta, 2),
        'utilidad_neta_uf': round(utilidad_neta, 2),
        'margen_bruto': round(margen_deseado, 2),
        'margen_neto': round(margen_neto, 2),
        'valor_uf': valor_uf,
        'detalle': detalle
    }

def reporte_productividad_persona(persona_id, periodo_meses=6):
    """
    Genera reporte de productividad individual con prorrateo correcto de costos e ingresos.
    
    Metodología:
    1. Calcula horas trabajadas por proyecto/cliente
    2. Prorratear costos según % de tiempo dedicado a cada proyecto
    3. Prorratear ingresos del proyecto según participación de la persona
    4. Calcular métricas de productividad individuales
    """
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=30 * periodo_meses)
    
    persona = Persona.query.get(persona_id)
    if not persona:
        return None
    
    # 1. HORAS TRABAJADAS TOTALES Y POR CLIENTE
    horas_por_cliente = db.session.query(
        RegistroHora.cliente_id,
        Cliente.nombre,
        func.sum(RegistroHora.horas).label('horas')
    ).join(Cliente)\
        .filter(RegistroHora.persona_id == persona_id)\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)\
        .group_by(RegistroHora.cliente_id, Cliente.nombre)\
        .all()
    
    horas_trabajadas_total = sum([h.horas for h in horas_por_cliente])
    
    # Horas esperadas
    if persona.tipo_jornada == 'full-time':
        horas_esperadas = HORAS_EFECTIVAS_MES * periodo_meses
    else:
        horas_esperadas = (HORAS_EFECTIVAS_MES / 2) * periodo_meses
    
    # 2. CALCULAR COSTOS TOTALES DE LA PERSONA
    costo_total_persona = horas_trabajadas_total * persona.costo_hora
    
    # 3. PRORRATEAR INGRESOS Y CALCULAR PRODUCTIVIDAD POR PROYECTO
    ingresos_prorrateados_total = 0
    margen_generado_total = 0
    detalles_por_proyecto = []
    
    for cliente_info in horas_por_cliente:
        cliente_id = cliente_info.cliente_id
        nombre_cliente = cliente_info.nombre
        horas_persona_cliente = cliente_info.horas
        
        # Porcentaje de participación de esta persona en el cliente
        porcentaje_participacion = (horas_persona_cliente / horas_trabajadas_total * 100) if horas_trabajadas_total > 0 else 0
        
        # Costo asignado a esta persona para este cliente
        costo_persona_cliente = horas_persona_cliente * persona.costo_hora
        
        # Obtener TODAS las horas trabajadas en este cliente (por todo el equipo)
        horas_totales_cliente = db.session.query(func.sum(RegistroHora.horas))\
            .filter(RegistroHora.cliente_id == cliente_id)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0
        
        # Obtener costos totales del cliente (todas las personas)
        costos_totales_cliente = db.session.query(
            func.sum(RegistroHora.horas * Persona.costo_hora)
        ).join(Persona)\
            .filter(RegistroHora.cliente_id == cliente_id)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0
        
        # Obtener ingresos totales del cliente (facturas)
        ingresos_totales_cliente = db.session.query(func.sum(Factura.monto_uf))\
            .filter(Factura.cliente_id == cliente_id)\
            .filter(Factura.fecha >= fecha_inicio)\
            .filter(Factura.fecha <= fecha_fin)\
            .scalar() or 0
        
        # PRORRATEO DE INGRESOS: Según participación en costos del cliente
        # Si esta persona representa el X% de los costos del cliente, 
        # se le asigna el X% de los ingresos
        if costos_totales_cliente > 0:
            porcentaje_costo_cliente = (costo_persona_cliente / costos_totales_cliente * 100)
            ingresos_prorrateados_cliente = ingresos_totales_cliente * (porcentaje_costo_cliente / 100)
        else:
            porcentaje_costo_cliente = 0
            ingresos_prorrateados_cliente = 0
        
        # Margen generado por esta persona en este cliente
        margen_persona_cliente = ingresos_prorrateados_cliente - costo_persona_cliente
        
        # ROI en este cliente
        roi_cliente = ((ingresos_prorrateados_cliente - costo_persona_cliente) / costo_persona_cliente * 100) if costo_persona_cliente > 0 else 0
        
        ingresos_prorrateados_total += ingresos_prorrateados_cliente
        margen_generado_total += margen_persona_cliente
        
        detalles_por_proyecto.append({
            'cliente': nombre_cliente,
            'horas_trabajadas': round(horas_persona_cliente, 2),
            'porcentaje_participacion': round(porcentaje_participacion, 2),
            'costo_asignado': round(costo_persona_cliente, 2),
            'ingresos_prorrateados': round(ingresos_prorrateados_cliente, 2),
            'margen_generado': round(margen_persona_cliente, 2),
            'roi_proyecto': round(roi_cliente, 2)
        })
    
    # 4. MÉTRICAS GLOBALES DE PRODUCTIVIDAD
    
    # Porcentaje de cumplimiento de horas
    porcentaje_cumplimiento = (horas_trabajadas_total / horas_esperadas * 100) if horas_esperadas > 0 else 0
    
    # ROI global de la persona
    roi_global = ((ingresos_prorrateados_total - costo_total_persona) / costo_total_persona * 100) if costo_total_persona > 0 else 0
    
    # Margen porcentual
    margen_porcentual = (margen_generado_total / ingresos_prorrateados_total * 100) if ingresos_prorrateados_total > 0 else 0
    
    # Productividad por hora (ingresos generados por hora trabajada)
    productividad_por_hora = ingresos_prorrateados_total / horas_trabajadas_total if horas_trabajadas_total > 0 else 0
    
    # Eficiencia de costos (cuánto ingreso genera por cada UF de costo)
    eficiencia_costos = ingresos_prorrateados_total / costo_total_persona if costo_total_persona > 0 else 0
    
    # 5. RECOMENDACIONES BASADAS EN MÉTRICAS
    
    # Criterios para aumento:
    # - ROI > 150% (genera 2.5x su costo)
    # - Cumplimiento de horas > 90%
    # - Margen porcentual > 20%
    recomendacion_aumento = 'Sí' if (roi_global > 150 and porcentaje_cumplimiento > 90 and margen_porcentual > 20) else 'Revisar' if roi_global > 100 else 'No'
    
    # Criterios para bono:
    # - Bono completo: ROI > 200%, cumplimiento > 95%, margen > 25%
    # - Bono parcial: ROI > 120%, cumplimiento > 85%, margen > 15%
    # - No corresponde: criterios inferiores
    if roi_global > 200 and porcentaje_cumplimiento > 95 and margen_porcentual > 25:
        recomendacion_bono = '100% - Desempeño excepcional'
    elif roi_global > 150 and porcentaje_cumplimiento > 90 and margen_porcentual > 20:
        recomendacion_bono = '75% - Desempeño sobresaliente'
    elif roi_global > 120 and porcentaje_cumplimiento > 85 and margen_porcentual > 15:
        recomendacion_bono = '50% - Buen desempeño'
    elif roi_global > 80 and porcentaje_cumplimiento > 80:
        recomendacion_bono = '25% - Desempeño adecuado'
    else:
        recomendacion_bono = 'No corresponde - Por debajo de expectativas'
    
    return {
        'persona': persona.nombre,
        'cargo': persona.cargo,
        'area': persona.area,
        'periodo_meses': periodo_meses,
        
        # Métricas de horas
        'horas_trabajadas': round(horas_trabajadas_total, 2),
        'horas_esperadas': round(horas_esperadas, 2),
        'porcentaje_cumplimiento': round(porcentaje_cumplimiento, 2),
        
        # Métricas financieras
        'costo_total': round(costo_total_persona, 2),
        'ingresos_prorrateados': round(ingresos_prorrateados_total, 2),
        'margen_generado': round(margen_generado_total, 2),
        'margen_porcentual': round(margen_porcentual, 2),
        
        # Métricas de eficiencia
        'roi_global': round(roi_global, 2),
        'productividad_por_hora': round(productividad_por_hora, 2),
        'eficiencia_costos': round(eficiencia_costos, 2),
        
        # Detalle por proyecto
        'proyectos': detalles_por_proyecto,
        
        # Recomendaciones
        'recomendacion_aumento': recomendacion_aumento,
        'recomendacion_bono': recomendacion_bono
    }

# ============= FUNCIONES DE PROYECTOS =============

def calcular_rentabilidad_proyecto(proyecto_id, periodo_meses=None):
    """
    Calcula la rentabilidad de un proyecto específico.
    Si periodo_meses es None, calcula desde inicio hasta fin del proyecto.
    """
    proyecto = Proyecto.query.get(proyecto_id)
    if not proyecto:
        return None

    # Determinar fechas del análisis
    if periodo_meses:
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30 * periodo_meses)
    else:
        fecha_inicio = proyecto.fecha_inicio or datetime.now().date() - timedelta(days=365)
        fecha_fin = proyecto.fecha_fin or datetime.now().date()

    # Calcular costos (horas trabajadas * costo por hora)
    horas_query = db.session.query(
        func.sum(RegistroHora.horas * Persona.costo_hora)
    ).join(Persona)\
        .filter(RegistroHora.proyecto_id == proyecto_id)\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)

    costos_totales = horas_query.scalar() or 0

    # Calcular total de horas trabajadas
    total_horas = db.session.query(func.sum(RegistroHora.horas))\
        .filter(RegistroHora.proyecto_id == proyecto_id)\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)\
        .scalar() or 0

    # Calcular ingresos (facturas del proyecto)
    ingresos_query = db.session.query(func.sum(Factura.monto_uf))\
        .filter(Factura.proyecto_id == proyecto_id)\
        .filter(Factura.fecha >= fecha_inicio)\
        .filter(Factura.fecha <= fecha_fin)

    ingresos_totales_uf = ingresos_query.scalar() or 0

    # Obtener valor UF
    valor_uf = obtener_uf_actual()
    ingresos_totales_pesos = ingresos_totales_uf * valor_uf
    costos_totales_pesos = costos_totales * valor_uf

    # Calcular utilidad y margen
    utilidad_bruta = ingresos_totales_uf - costos_totales
    margen = (utilidad_bruta / ingresos_totales_uf * 100) if ingresos_totales_uf > 0 else 0

    # Calcular utilidad después de impuestos
    utilidad_despues_impuestos = utilidad_bruta * (1 - IMPUESTO)

    # ROI del proyecto
    roi_proyecto = (utilidad_bruta / costos_totales * 100) if costos_totales > 0 else 0

    # Comparación con margen objetivo
    diferencia_margen = margen - proyecto.margen_objetivo if proyecto.margen_objetivo else 0

    # Estado de rentabilidad
    if margen >= (proyecto.margen_objetivo or 12.5):
        estado_rentabilidad = 'optimo'
    elif margen >= (proyecto.margen_objetivo or 12.5) * 0.8:
        estado_rentabilidad = 'aceptable'
    else:
        estado_rentabilidad = 'bajo'

    # Equipo del proyecto
    equipo = db.session.query(
        Persona.nombre,
        Persona.cargo,
        func.sum(RegistroHora.horas).label('horas')
    ).join(RegistroHora)\
        .filter(RegistroHora.proyecto_id == proyecto_id)\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)\
        .group_by(Persona.id, Persona.nombre, Persona.cargo)\
        .all()

    detalle_equipo = [
        {
            'persona': e.nombre,
            'cargo': e.cargo,
            'horas': round(e.horas, 2),
            'porcentaje': round((e.horas / total_horas * 100) if total_horas > 0 else 0, 2)
        }
        for e in equipo
    ]

    return {
        'proyecto_id': proyecto.id,
        'proyecto_nombre': proyecto.nombre,
        'proyecto_codigo': proyecto.codigo,
        'cliente': proyecto.cliente.nombre,
        'fecha_inicio': fecha_inicio.isoformat(),
        'fecha_fin': fecha_fin.isoformat(),
        'estado': proyecto.estado,

        # Financiero
        'ingresos_uf': round(ingresos_totales_uf, 2),
        'ingresos_pesos': round(ingresos_totales_pesos, 0),
        'costos_uf': round(costos_totales, 2),
        'costos_pesos': round(costos_totales_pesos, 0),
        'utilidad_bruta_uf': round(utilidad_bruta, 2),
        'utilidad_bruta_pesos': round(utilidad_bruta * valor_uf, 0),
        'utilidad_neta_uf': round(utilidad_despues_impuestos, 2),
        'utilidad_neta_pesos': round(utilidad_despues_impuestos * valor_uf, 0),

        # Métricas
        'margen': round(margen, 2),
        'roi': round(roi_proyecto, 2),
        'margen_objetivo': round(proyecto.margen_objetivo, 2) if proyecto.margen_objetivo else 12.5,
        'diferencia_margen': round(diferencia_margen, 2),
        'estado_rentabilidad': estado_rentabilidad,

        # Presupuesto
        'presupuesto_uf': round(proyecto.presupuesto_uf, 2) if proyecto.presupuesto_uf else 0,
        'desviacion_presupuesto': round(ingresos_totales_uf - proyecto.presupuesto_uf, 2) if proyecto.presupuesto_uf else 0,

        # Recursos
        'total_horas': round(total_horas, 2),
        'equipo': detalle_equipo,
        'valor_uf': valor_uf
    }

def reporte_productividad_persona_en_proyecto(persona_id, proyecto_id, periodo_meses=None):
    """
    Genera reporte de productividad de una persona en un proyecto específico.
    """
    persona = Persona.query.get(persona_id)
    proyecto = Proyecto.query.get(proyecto_id)

    if not persona or not proyecto:
        return None

    # Determinar fechas
    if periodo_meses:
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30 * periodo_meses)
    else:
        fecha_inicio = proyecto.fecha_inicio or datetime.now().date() - timedelta(days=365)
        fecha_fin = proyecto.fecha_fin or datetime.now().date()

    # Horas trabajadas por la persona en el proyecto
    horas_persona = db.session.query(func.sum(RegistroHora.horas))\
        .filter(RegistroHora.persona_id == persona_id)\
        .filter(RegistroHora.proyecto_id == proyecto_id)\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)\
        .scalar() or 0

    # Costo de la persona en el proyecto
    costo_persona = horas_persona * persona.costo_hora

    # Costos totales del proyecto
    costos_totales_proyecto = db.session.query(
        func.sum(RegistroHora.horas * Persona.costo_hora)
    ).join(Persona)\
        .filter(RegistroHora.proyecto_id == proyecto_id)\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)\
        .scalar() or 0

    # Ingresos totales del proyecto
    ingresos_totales_proyecto = db.session.query(func.sum(Factura.monto_uf))\
        .filter(Factura.proyecto_id == proyecto_id)\
        .filter(Factura.fecha >= fecha_inicio)\
        .filter(Factura.fecha <= fecha_fin)\
        .scalar() or 0

    # Prorrateo de ingresos según participación en costos
    if costos_totales_proyecto > 0:
        porcentaje_participacion = (costo_persona / costos_totales_proyecto * 100)
        ingresos_prorrateados = ingresos_totales_proyecto * (porcentaje_participacion / 100)
    else:
        porcentaje_participacion = 0
        ingresos_prorrateados = 0

    # Margen generado
    margen_generado = ingresos_prorrateados - costo_persona

    # ROI individual en el proyecto
    roi_persona = (margen_generado / costo_persona * 100) if costo_persona > 0 else 0

    # Margen porcentual
    margen_porcentual = (margen_generado / ingresos_prorrateados * 100) if ingresos_prorrateados > 0 else 0

    # Eficiencia (cuánto genera por cada UF de costo)
    eficiencia = ingresos_prorrateados / costo_persona if costo_persona > 0 else 0

    # Productividad por hora
    productividad_hora = ingresos_prorrateados / horas_persona if horas_persona > 0 else 0

    return {
        'persona': persona.nombre,
        'cargo': persona.cargo,
        'proyecto': proyecto.nombre,
        'proyecto_codigo': proyecto.codigo,
        'cliente': proyecto.cliente.nombre,

        # Horas
        'horas_trabajadas': round(horas_persona, 2),
        'porcentaje_participacion': round(porcentaje_participacion, 2),

        # Financiero
        'costo_asignado': round(costo_persona, 2),
        'ingresos_prorrateados': round(ingresos_prorrateados, 2),
        'margen_generado': round(margen_generado, 2),
        'margen_porcentual': round(margen_porcentual, 2),

        # Métricas
        'roi': round(roi_persona, 2),
        'eficiencia': round(eficiencia, 2),
        'productividad_por_hora': round(productividad_hora, 2),

        # Contexto del proyecto
        'costos_totales_proyecto': round(costos_totales_proyecto, 2),
        'ingresos_totales_proyecto': round(ingresos_totales_proyecto, 2)
    }

def listar_proyectos_persona(persona_id):
    """Lista todos los proyectos en los que participa una persona"""
    proyectos = db.session.query(
        Proyecto.id,
        Proyecto.nombre,
        Proyecto.codigo,
        Proyecto.estado,
        Cliente.nombre.label('cliente'),
        AsignacionProyecto.rol_proyecto,
        func.sum(RegistroHora.horas).label('horas_trabajadas')
    ).join(AsignacionProyecto, AsignacionProyecto.proyecto_id == Proyecto.id)\
        .join(Cliente, Cliente.id == Proyecto.cliente_id)\
        .outerjoin(RegistroHora, and_(
            RegistroHora.proyecto_id == Proyecto.id,
            RegistroHora.persona_id == persona_id
        ))\
        .filter(AsignacionProyecto.persona_id == persona_id)\
        .group_by(Proyecto.id, Proyecto.nombre, Proyecto.codigo, Proyecto.estado,
                  Cliente.nombre, AsignacionProyecto.rol_proyecto)\
        .all()

    return [
        {
            'proyecto_id': p.id,
            'proyecto': p.nombre,
            'codigo': p.codigo,
            'cliente': p.cliente,
            'estado': p.estado,
            'rol': p.rol_proyecto,
            'horas': round(p.horas_trabajadas, 2) if p.horas_trabajadas else 0
        }
        for p in proyectos
    ]

def listar_proyectos_cliente(cliente_id):
    """Lista todos los proyectos de un cliente"""
    proyectos = Proyecto.query.filter_by(cliente_id=cliente_id).all()

    resultado = []
    for proyecto in proyectos:
        # Calcular rentabilidad básica
        rent = calcular_rentabilidad_proyecto(proyecto.id)
        if rent:
            resultado.append({
                'proyecto_id': proyecto.id,
                'nombre': proyecto.nombre,
                'codigo': proyecto.codigo,
                'estado': proyecto.estado,
                'fecha_inicio': proyecto.fecha_inicio.isoformat() if proyecto.fecha_inicio else None,
                'fecha_fin': proyecto.fecha_fin.isoformat() if proyecto.fecha_fin else None,
                'ingresos_uf': rent['ingresos_uf'],
                'margen': rent['margen'],
                'roi': rent['roi'],
                'estado_rentabilidad': rent['estado_rentabilidad']
            })

    return resultado

def comparar_proyectos_cliente(cliente_id):
    """Compara la rentabilidad de todos los proyectos de un cliente"""
    proyectos = listar_proyectos_cliente(cliente_id)

    if not proyectos:
        return None

    # Ordenar por rentabilidad
    proyectos_ordenados = sorted(proyectos, key=lambda x: x['margen'], reverse=True)

    # Calcular totales
    total_ingresos = sum(p['ingresos_uf'] for p in proyectos)
    margen_promedio = sum(p['margen'] for p in proyectos) / len(proyectos) if proyectos else 0

    return {
        'cliente_id': cliente_id,
        'cliente': Cliente.query.get(cliente_id).nombre,
        'total_proyectos': len(proyectos),
        'total_ingresos_uf': round(total_ingresos, 2),
        'margen_promedio': round(margen_promedio, 2),
        'proyecto_mas_rentable': proyectos_ordenados[0] if proyectos_ordenados else None,
        'proyecto_menos_rentable': proyectos_ordenados[-1] if proyectos_ordenados else None,
        'proyectos': proyectos_ordenados
    }

def proyectos_en_riesgo():
    """Identifica proyectos con baja rentabilidad o sobre presupuesto"""
    proyectos_activos = Proyecto.query.filter_by(estado='activo').all()

    riesgo = []
    for proyecto in proyectos_activos:
        rent = calcular_rentabilidad_proyecto(proyecto.id)
        if rent:
            razones = []

            # Margen bajo
            if rent['margen'] < (proyecto.margen_objetivo or 12.5) * 0.8:
                razones.append(f"Margen bajo ({rent['margen']:.1f}% vs objetivo {proyecto.margen_objetivo or 12.5}%)")

            # Sobre presupuesto
            if proyecto.presupuesto_uf and rent['ingresos_uf'] > proyecto.presupuesto_uf * 1.1:
                razones.append(f"Sobre presupuesto ({rent['desviacion_presupuesto']:.1f} UF)")

            # Pérdidas
            if rent['utilidad_bruta_uf'] < 0:
                razones.append(f"Con pérdidas ({rent['utilidad_bruta_uf']:.1f} UF)")

            if razones:
                riesgo.append({
                    'proyecto': proyecto.nombre,
                    'codigo': proyecto.codigo,
                    'cliente': proyecto.cliente.nombre,
                    'razones': razones,
                    'margen': rent['margen'],
                    'roi': rent['roi']
                })

    return sorted(riesgo, key=lambda x: x['margen'])

def analisis_detallado_cliente(cliente_id, meses=12):
    """
    Análisis exhaustivo de rentabilidad de un cliente con desglose mensual,
    por proyecto, personas involucradas y tendencias.
    """
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return None

    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=30 * meses)

    # Obtener todos los proyectos del cliente
    proyectos = Proyecto.query.filter_by(cliente_id=cliente_id).all()

    # Análisis por mes
    analisis_mensual = []
    mes_actual = fecha_inicio.replace(day=1)

    while mes_actual <= fecha_fin:
        mes_fin = (mes_actual.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        # Horas del mes
        horas_mes = db.session.query(func.sum(RegistroHora.horas))\
            .join(Proyecto)\
            .filter(Proyecto.cliente_id == cliente_id)\
            .filter(RegistroHora.fecha >= mes_actual)\
            .filter(RegistroHora.fecha <= mes_fin)\
            .scalar() or 0

        # Costos del mes
        costos_mes = db.session.query(func.sum(RegistroHora.horas * Persona.costo_hora))\
            .join(Persona).join(Proyecto)\
            .filter(Proyecto.cliente_id == cliente_id)\
            .filter(RegistroHora.fecha >= mes_actual)\
            .filter(RegistroHora.fecha <= mes_fin)\
            .scalar() or 0

        # Ingresos del mes
        ingresos_mes = db.session.query(func.sum(Factura.monto_uf))\
            .filter(Factura.cliente_id == cliente_id)\
            .filter(Factura.fecha >= mes_actual)\
            .filter(Factura.fecha <= mes_fin)\
            .scalar() or 0

        # Personas activas del mes
        personas_mes = db.session.query(func.count(func.distinct(RegistroHora.persona_id)))\
            .join(Proyecto)\
            .filter(Proyecto.cliente_id == cliente_id)\
            .filter(RegistroHora.fecha >= mes_actual)\
            .filter(RegistroHora.fecha <= mes_fin)\
            .scalar() or 0

        margen_mes = ((ingresos_mes - costos_mes) / ingresos_mes * 100) if ingresos_mes > 0 else 0

        analisis_mensual.append({
            'mes': mes_actual.strftime('%Y-%m'),
            'mes_nombre': mes_actual.strftime('%B %Y'),
            'horas': round(horas_mes, 1),
            'costos_uf': round(costos_mes, 2),
            'ingresos_uf': round(ingresos_mes, 2),
            'margen': round(margen_mes, 1),
            'personas': personas_mes,
            'rentable': margen_mes > 0
        })

        # Siguiente mes
        mes_actual = (mes_actual.replace(day=28) + timedelta(days=4)).replace(day=1)

    # Análisis por proyecto
    analisis_proyectos = []
    for proyecto in proyectos:
        rent = calcular_rentabilidad_proyecto(proyecto.id, periodo_meses=meses)
        if rent and rent['total_horas'] > 0:
            # Horas estimadas vs reales
            horas_estimadas = db.session.query(func.sum(AsignacionProyecto.horas_estimadas))\
                .filter(AsignacionProyecto.proyecto_id == proyecto.id)\
                .filter(AsignacionProyecto.activo == True)\
                .scalar() or 0

            desviacion_horas = rent['total_horas'] - horas_estimadas if horas_estimadas > 0 else 0
            sobre_demandante = desviacion_horas > (horas_estimadas * 0.2) if horas_estimadas > 0 else False

            analisis_proyectos.append({
                'proyecto_id': proyecto.id,
                'nombre': proyecto.nombre,
                'codigo': proyecto.codigo,
                'estado': proyecto.estado,
                'horas_reales': rent['total_horas'],
                'horas_estimadas': round(horas_estimadas, 1),
                'desviacion_horas': round(desviacion_horas, 1),
                'desviacion_porcentaje': round((desviacion_horas / horas_estimadas * 100) if horas_estimadas > 0 else 0, 1),
                'sobre_demandante': sobre_demandante,
                'ingresos_uf': rent['ingresos_uf'],
                'costos_uf': rent['costos_uf'],
                'margen': rent['margen'],
                'roi': rent['roi'],
                'personas': len(rent['equipo']),
                'estado_rentabilidad': rent['estado_rentabilidad']
            })

    # Ordenar proyectos por horas reales (descendente)
    analisis_proyectos.sort(key=lambda x: x['horas_reales'], reverse=True)

    # Análisis de personas más involucradas
    # Consulta simplificada: personas por cliente (no necesariamente por proyecto)
    personas_involucradas = db.session.query(
        Persona.id,
        Persona.nombre,
        Persona.cargo,
        func.sum(RegistroHora.horas).label('total_horas')
    ).select_from(Persona)\
        .join(RegistroHora, RegistroHora.persona_id == Persona.id)\
        .filter(RegistroHora.cliente_id == cliente_id)\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)\
        .group_by(Persona.id, Persona.nombre, Persona.cargo)\
        .order_by(func.sum(RegistroHora.horas).desc())\
        .limit(10)\
        .all()

    # Contar proyectos para cada persona
    def contar_proyectos_persona(persona_id):
        return db.session.query(func.count(func.distinct(RegistroHora.proyecto_id)))\
            .filter(RegistroHora.persona_id == persona_id)\
            .filter(RegistroHora.cliente_id == cliente_id)\
            .filter(RegistroHora.proyecto_id.isnot(None))\
            .scalar() or 0

    top_personas = [
        {
            'persona_id': p.id,
            'nombre': p.nombre,
            'cargo': p.cargo,
            'total_horas': round(p.total_horas, 1),
            'proyectos_count': contar_proyectos_persona(p.id)
        }
        for p in personas_involucradas
    ]

    # Totales generales
    total_horas = sum(m['horas'] for m in analisis_mensual)
    total_costos = sum(m['costos_uf'] for m in analisis_mensual)
    total_ingresos = sum(m['ingresos_uf'] for m in analisis_mensual)
    margen_promedio = ((total_ingresos - total_costos) / total_ingresos * 100) if total_ingresos > 0 else 0

    # Meses rentables vs no rentables
    meses_rentables = len([m for m in analisis_mensual if m['rentable']])
    meses_totales = len(analisis_mensual)

    # Proyectos sobre-demandantes
    proyectos_sobre_demandantes = [p for p in analisis_proyectos if p['sobre_demandante']]

    # Proyecto más/menos rentable
    proyecto_mas_rentable = max(analisis_proyectos, key=lambda x: x['margen']) if analisis_proyectos else None
    proyecto_menos_rentable = min(analisis_proyectos, key=lambda x: x['margen']) if analisis_proyectos else None

    # Tendencia (comparar primera mitad vs segunda mitad)
    mitad = len(analisis_mensual) // 2
    if mitad > 0:
        margen_primera_mitad = sum(m['margen'] for m in analisis_mensual[:mitad]) / mitad
        margen_segunda_mitad = sum(m['margen'] for m in analisis_mensual[mitad:]) / (len(analisis_mensual) - mitad)
        tendencia = 'mejorando' if margen_segunda_mitad > margen_primera_mitad else 'empeorando' if margen_segunda_mitad < margen_primera_mitad else 'estable'
    else:
        tendencia = 'insuficiente_datos'

    valor_uf = obtener_uf_actual()

    return {
        'cliente_id': cliente.id,
        'cliente_nombre': cliente.nombre,
        'cliente_tipo': cliente.tipo,
        'cliente_area': cliente.area,
        'periodo': {
            'inicio': fecha_inicio.isoformat(),
            'fin': fecha_fin.isoformat(),
            'meses': meses
        },
        'totales': {
            'horas': round(total_horas, 1),
            'costos_uf': round(total_costos, 2),
            'costos_pesos': round(total_costos * valor_uf, 0),
            'ingresos_uf': round(total_ingresos, 2),
            'ingresos_pesos': round(total_ingresos * valor_uf, 0),
            'margen': round(margen_promedio, 1),
            'meses_rentables': meses_rentables,
            'meses_totales': meses_totales,
            'porcentaje_meses_rentables': round((meses_rentables / meses_totales * 100) if meses_totales > 0 else 0, 1)
        },
        'analisis_mensual': analisis_mensual,
        'proyectos': analisis_proyectos,
        'proyectos_sobre_demandantes': proyectos_sobre_demandantes,
        'top_personas': top_personas,
        'insights': {
            'proyecto_mas_rentable': proyecto_mas_rentable,
            'proyecto_menos_rentable': proyecto_menos_rentable,
            'tendencia': tendencia,
            'num_proyectos_activos': len([p for p in proyectos if p.estado == 'activo']),
            'num_proyectos_totales': len(proyectos)
        },
        'valor_uf': valor_uf
    }

# ============= RUTAS DE LA APLICACIÓN =============

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Hashear la contraseña ingresada
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Verificar credenciales
        if username in USERS and USERS[username] == password_hash:
            session['logged_in'] = True
            session['username'] = username
            flash(f'Bienvenido {username}!', 'success')

            # Redirigir a la página solicitada o al index
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con indicadores clave"""
    capacidad = calcular_capacidad_equipo(periodo_meses=1)
    sin_horas = personas_sin_horas_recientes()
    top_clientes = ranking_clientes_rentables(top=5)
    areas_rent = rentabilidad_por_area()
    
    return render_template('dashboard.html', 
                         capacidad=capacidad,
                         sin_horas=sin_horas,
                         top_clientes=top_clientes,
                         areas_rentabilidad=areas_rent)

# Rutas para personas
@app.route('/personas')
@login_required
def listar_personas():
    personas = Persona.query.filter_by(activo=True).all()
    return render_template('personas.html', personas=personas)

@app.route('/personas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_persona():
    if request.method == 'POST':
        persona = Persona(
            nombre=request.form['nombre'],
            email=request.form['email'],
            cargo=request.form['cargo'],
            tipo_jornada=request.form['tipo_jornada'],
            area=request.form['area'],
            costo_hora=float(request.form['costo_hora']),
            sueldo_mensual=float(request.form.get('sueldo_mensual', 0))
        )
        db.session.add(persona)
        db.session.commit()
        return redirect(url_for('listar_personas'))
    return render_template('persona_form.html', persona=None)

@app.route('/personas/<int:persona_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_persona(persona_id):
    persona = Persona.query.get_or_404(persona_id)

    if request.method == 'POST':
        persona.nombre = request.form['nombre']
        persona.email = request.form['email']
        persona.cargo = request.form['cargo']
        persona.tipo_jornada = request.form['tipo_jornada']
        persona.area = request.form['area']
        persona.costo_hora = float(request.form['costo_hora'])
        persona.sueldo_mensual = float(request.form.get('sueldo_mensual', 0))

        db.session.commit()
        return redirect(url_for('listar_personas'))

    return render_template('persona_form.html', persona=persona)

@app.route('/personas/<int:persona_id>/eliminar', methods=['POST'])
@login_required
def eliminar_persona(persona_id):
    persona = Persona.query.get_or_404(persona_id)
    persona.activo = False
    db.session.commit()
    return redirect(url_for('listar_personas'))

# Rutas para clientes
@app.route('/clientes')
@login_required
def listar_clientes():
    clientes = Cliente.query.filter_by(activo=True).all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    if request.method == 'POST':
        cliente = Cliente(
            nombre=request.form['nombre'],
            tipo=request.form['tipo'],
            area=request.form['area'],
            fecha_inicio=datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()
        )
        db.session.add(cliente)
        db.session.commit()
        return redirect(url_for('listar_clientes'))
    return render_template('cliente_form.html', cliente=None)

@app.route('/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.tipo = request.form['tipo']
        cliente.area = request.form['area']
        cliente.fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()

        db.session.commit()
        return redirect(url_for('listar_clientes'))

    return render_template('cliente_form.html', cliente=cliente)

@app.route('/clientes/<int:cliente_id>/eliminar', methods=['POST'])
@login_required
def eliminar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    cliente.activo = False
    db.session.commit()
    return redirect(url_for('listar_clientes'))

@app.route('/clientes/<int:cliente_id>/rentabilidad')
@login_required
def cliente_rentabilidad(cliente_id):
    """Vista detallada de rentabilidad de un cliente con gráficos"""
    cliente = Cliente.query.get_or_404(cliente_id)
    meses = request.args.get('meses', 12, type=int)
    analisis = analisis_detallado_cliente(cliente_id, meses)

    return render_template('cliente_rentabilidad.html',
                         cliente=cliente,
                         analisis=analisis,
                         meses=meses)

@app.route('/api/clientes/<int:cliente_id>/analisis')
@login_required
def api_analisis_cliente(cliente_id):
    """API endpoint para análisis detallado de cliente"""
    meses = request.args.get('meses', 12, type=int)
    analisis = analisis_detallado_cliente(cliente_id, meses)
    return jsonify(analisis)

# Ruta de Productividad
@app.route('/productividad')
@login_required
def productividad():
    """Vista general de productividad y rentabilidad con desglose por cliente, área y servicio"""
    meses = request.args.get('meses', 12, type=int)

    # Calcular fechas
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=meses * 30)

    # 1. RENTABILIDAD TOTAL
    total_horas = db.session.query(func.sum(RegistroHora.horas))\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)\
        .scalar() or 0

    total_costos_uf = db.session.query(func.sum(RegistroHora.horas * Persona.costo_hora))\
        .select_from(RegistroHora)\
        .join(Persona, RegistroHora.persona_id == Persona.id)\
        .filter(RegistroHora.fecha >= fecha_inicio)\
        .filter(RegistroHora.fecha <= fecha_fin)\
        .scalar() or 0

    total_ingresos_uf = db.session.query(func.sum(Factura.monto_uf))\
        .filter(Factura.fecha >= fecha_inicio)\
        .filter(Factura.fecha <= fecha_fin)\
        .scalar() or 0

    margen_total = ((total_ingresos_uf - total_costos_uf) / total_ingresos_uf * 100) if total_ingresos_uf > 0 else 0

    # 2. RENTABILIDAD POR CLIENTE
    clientes_data = []
    clientes = Cliente.query.filter_by(activo=True).all()

    for cliente in clientes:
        horas_cliente = db.session.query(func.sum(RegistroHora.horas))\
            .filter(RegistroHora.cliente_id == cliente.id)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0

        if horas_cliente == 0:
            continue

        costos_cliente = db.session.query(func.sum(RegistroHora.horas * Persona.costo_hora))\
            .select_from(RegistroHora)\
            .join(Persona, RegistroHora.persona_id == Persona.id)\
            .filter(RegistroHora.cliente_id == cliente.id)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0

        ingresos_cliente = db.session.query(func.sum(Factura.monto_uf))\
            .filter(Factura.cliente_id == cliente.id)\
            .filter(Factura.fecha >= fecha_inicio)\
            .filter(Factura.fecha <= fecha_fin)\
            .scalar() or 0

        margen_cliente = ((ingresos_cliente - costos_cliente) / ingresos_cliente * 100) if ingresos_cliente > 0 else 0
        margen_uf = ingresos_cliente - costos_cliente

        clientes_data.append({
            'id': cliente.id,
            'nombre': cliente.nombre,
            'area': cliente.area,
            'tipo': cliente.tipo,
            'horas': round(horas_cliente, 1),
            'ingresos_uf': round(ingresos_cliente, 2),
            'costos_uf': round(costos_cliente, 2),
            'margen_porcentaje': round(margen_cliente, 1),
            'margen_uf': round(margen_uf, 2)
        })

    # Ordenar por margen UF descendente
    clientes_data.sort(key=lambda x: x['margen_uf'], reverse=True)

    # 3. RENTABILIDAD POR ÁREA
    areas_data = {}
    for area in ['Externas', 'Internas', 'Asuntos Públicos', 'Redes sociales', 'Diseño']:
        horas_area = db.session.query(func.sum(RegistroHora.horas))\
            .join(Cliente, RegistroHora.cliente_id == Cliente.id)\
            .filter(Cliente.area == area)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0

        if horas_area == 0:
            continue

        costos_area = db.session.query(func.sum(RegistroHora.horas * Persona.costo_hora))\
            .select_from(RegistroHora)\
            .join(Persona, RegistroHora.persona_id == Persona.id)\
            .join(Cliente, RegistroHora.cliente_id == Cliente.id)\
            .filter(Cliente.area == area)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0

        ingresos_area = db.session.query(func.sum(Factura.monto_uf))\
            .join(Cliente, Factura.cliente_id == Cliente.id)\
            .filter(Cliente.area == area)\
            .filter(Factura.fecha >= fecha_inicio)\
            .filter(Factura.fecha <= fecha_fin)\
            .scalar() or 0

        margen_area = ((ingresos_area - costos_area) / ingresos_area * 100) if ingresos_area > 0 else 0

        areas_data[area] = {
            'horas': round(horas_area, 1),
            'ingresos_uf': round(ingresos_area, 2),
            'costos_uf': round(costos_area, 2),
            'margen_porcentaje': round(margen_area, 1),
            'margen_uf': round(ingresos_area - costos_area, 2)
        }

    # 4. RENTABILIDAD POR SERVICIO
    servicios_data = []
    servicios = Servicio.query.all()

    for servicio in servicios:
        horas_servicio = db.session.query(func.sum(RegistroHora.horas))\
            .filter(RegistroHora.servicio_id == servicio.id)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0

        if horas_servicio == 0:
            continue

        costos_servicio = db.session.query(func.sum(RegistroHora.horas * Persona.costo_hora))\
            .select_from(RegistroHora)\
            .join(Persona, RegistroHora.persona_id == Persona.id)\
            .filter(RegistroHora.servicio_id == servicio.id)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0

        # Para ingresos por servicio, necesitamos prorratear las facturas
        # Simplificación: usar costos como base
        participacion = costos_servicio / total_costos_uf if total_costos_uf > 0 else 0
        ingresos_servicio = total_ingresos_uf * participacion

        margen_servicio = ((ingresos_servicio - costos_servicio) / ingresos_servicio * 100) if ingresos_servicio > 0 else 0

        servicios_data.append({
            'nombre': servicio.nombre,
            'area': servicio.area,
            'horas': round(horas_servicio, 1),
            'ingresos_uf': round(ingresos_servicio, 2),
            'costos_uf': round(costos_servicio, 2),
            'margen_porcentaje': round(margen_servicio, 1),
            'margen_uf': round(ingresos_servicio - costos_servicio, 2)
        })

    # Ordenar por horas descendente
    servicios_data.sort(key=lambda x: x['horas'], reverse=True)

    return render_template('productividad.html',
                         meses=meses,
                         total={
                             'horas': round(total_horas, 1),
                             'ingresos_uf': round(total_ingresos_uf, 2),
                             'costos_uf': round(total_costos_uf, 2),
                             'margen_porcentaje': round(margen_total, 1),
                             'margen_uf': round(total_ingresos_uf - total_costos_uf, 2)
                         },
                         clientes=clientes_data,
                         areas=areas_data,
                         servicios=servicios_data)

# Rutas para proyectos
@app.route('/proyectos')
@login_required
def listar_proyectos():
    proyectos = Proyecto.query.order_by(Proyecto.estado.asc(), Proyecto.fecha_inicio.desc()).all()
    return render_template('proyectos.html', proyectos=proyectos)

@app.route('/proyectos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proyecto():
    if request.method == 'POST':
        # Generar código si no se proporciona
        codigo = request.form.get('codigo')
        if not codigo:
            cliente = Cliente.query.get(request.form['cliente_id'])
            prefijo = cliente.nombre[:3].upper().replace(' ', '')
            año = datetime.now().year
            # Buscar el siguiente número disponible
            numero = 1
            while Proyecto.query.filter_by(codigo=f"{prefijo}-PRY-{año}-{numero:02d}").first():
                numero += 1
            codigo = f"{prefijo}-PRY-{año}-{numero:02d}"

        proyecto = Proyecto(
            cliente_id=int(request.form['cliente_id']),
            nombre=request.form['nombre'],
            codigo=codigo,
            servicio_id=int(request.form['servicio_id']) if request.form.get('servicio_id') else None,
            tipo=request.form.get('tipo', 'permanente'),
            fecha_inicio=datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date() if request.form.get('fecha_inicio') else None,
            fecha_fin=datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date() if request.form.get('fecha_fin') else None,
            presupuesto_uf=float(request.form['presupuesto_uf']) if request.form.get('presupuesto_uf') else None,
            estado=request.form.get('estado', 'activo'),
            descripcion=request.form.get('descripcion', ''),
            margen_objetivo=float(request.form.get('margen_objetivo', 12.5))
        )
        db.session.add(proyecto)
        db.session.commit()
        return redirect(url_for('listar_proyectos'))

    clientes = Cliente.query.filter_by(activo=True).all()
    servicios = Servicio.query.all()
    return render_template('proyecto_form.html', clientes=clientes, servicios=servicios)

@app.route('/proyectos/<int:proyecto_id>')
@login_required
def detalle_proyecto(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    rentabilidad = calcular_rentabilidad_proyecto(proyecto_id)
    asignaciones = AsignacionProyecto.query.filter_by(proyecto_id=proyecto_id, activo=True).all()

    return render_template('proyecto_detalle.html',
                         proyecto=proyecto,
                         rentabilidad=rentabilidad,
                         asignaciones=asignaciones)

@app.route('/proyectos/<int:proyecto_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_proyecto(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)

    if request.method == 'POST':
        proyecto.nombre = request.form['nombre']
        proyecto.codigo = request.form.get('codigo') or proyecto.codigo
        proyecto.servicio_id = int(request.form['servicio_id']) if request.form.get('servicio_id') else None
        proyecto.tipo = request.form.get('tipo', 'permanente')
        proyecto.fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date() if request.form.get('fecha_inicio') else None
        proyecto.fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date() if request.form.get('fecha_fin') else None
        proyecto.presupuesto_uf = float(request.form['presupuesto_uf']) if request.form.get('presupuesto_uf') else None
        proyecto.estado = request.form.get('estado', 'activo')
        proyecto.descripcion = request.form.get('descripcion', '')
        proyecto.margen_objetivo = float(request.form.get('margen_objetivo', 12.5))

        db.session.commit()
        return redirect(url_for('detalle_proyecto', proyecto_id=proyecto_id))

    clientes = Cliente.query.filter_by(activo=True).all()
    servicios = Servicio.query.all()
    return render_template('proyecto_form.html', clientes=clientes, servicios=servicios, proyecto=proyecto)

@app.route('/proyectos/<int:proyecto_id>/asignar', methods=['GET', 'POST'])
@login_required
def asignar_persona_proyecto(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)

    if request.method == 'POST':
        asignacion = AsignacionProyecto(
            persona_id=int(request.form['persona_id']),
            proyecto_id=proyecto_id,
            rol_proyecto=request.form.get('rol_proyecto', 'colaborador'),
            horas_estimadas=float(request.form.get('horas_estimadas', 0)),
            costo_hora_proyecto=float(request.form['costo_hora_proyecto']) if request.form.get('costo_hora_proyecto') else None,
            fecha_inicio=datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date() if request.form.get('fecha_inicio') else datetime.now().date(),
            activo=True
        )
        db.session.add(asignacion)
        db.session.commit()
        return redirect(url_for('detalle_proyecto', proyecto_id=proyecto_id))

    personas = Persona.query.filter_by(activo=True).all()
    return render_template('asignar_proyecto.html', proyecto=proyecto, personas=personas)

@app.route('/proyectos/<int:proyecto_id>/asignaciones/<int:asignacion_id>/eliminar', methods=['POST'])
@login_required
def eliminar_asignacion(proyecto_id, asignacion_id):
    asignacion = AsignacionProyecto.query.get_or_404(asignacion_id)
    asignacion.activo = False
    db.session.commit()
    return redirect(url_for('detalle_proyecto', proyecto_id=proyecto_id))

# Rutas para registro de horas
@app.route('/horas')
@login_required
def listar_horas():
    horas = RegistroHora.query.order_by(RegistroHora.fecha.desc()).limit(100).all()
    return render_template('horas.html', horas=horas)

@app.route('/horas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_hora():
    if request.method == 'POST':
        hora = RegistroHora(
            persona_id=int(request.form['persona_id']),
            cliente_id=int(request.form['cliente_id']),
            proyecto_id=int(request.form['proyecto_id']) if request.form.get('proyecto_id') else None,
            servicio_id=int(request.form['servicio_id']) if request.form.get('servicio_id') else None,
            tarea_id=int(request.form['tarea_id']) if request.form.get('tarea_id') else None,
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            horas=float(request.form['horas']),
            descripcion=request.form.get('descripcion', '')
        )
        db.session.add(hora)
        db.session.commit()
        return redirect(url_for('listar_horas'))

    personas = Persona.query.filter_by(activo=True).all()
    clientes = Cliente.query.filter_by(activo=True).all()
    proyectos = Proyecto.query.filter_by(estado='activo').all()
    servicios = Servicio.query.all()

    # Crear diccionario de tareas por servicio para JavaScript
    import json
    tareas_dict = {}
    for servicio in servicios:
        tareas_dict[servicio.id] = [
            {'id': t.id, 'nombre': t.nombre}
            for t in Tarea.query.filter_by(servicio_id=servicio.id).all()
        ]
    tareas_json = json.dumps(tareas_dict)

    return render_template('hora_form.html',
                         personas=personas,
                         clientes=clientes,
                         proyectos=proyectos,
                         servicios=servicios,
                         tareas_json=tareas_json,
                         today=datetime.now().strftime('%Y-%m-%d'))

# Rutas para servicios
@app.route('/servicios')
@login_required
def listar_servicios():
    servicios = Servicio.query.all()
    return render_template('servicios.html', servicios=servicios)

@app.route('/servicios/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_servicio():
    if request.method == 'POST':
        servicio = Servicio(
            nombre=request.form['nombre'],
            area=request.form.get('area', '')
        )
        db.session.add(servicio)
        db.session.commit()
        return redirect(url_for('listar_servicios'))
    return render_template('servicio_form.html', servicio=None)

@app.route('/servicios/<int:servicio_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_servicio(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)

    if request.method == 'POST':
        servicio.nombre = request.form['nombre']
        servicio.area = request.form.get('area', '')

        db.session.commit()
        return redirect(url_for('listar_servicios'))

    return render_template('servicio_form.html', servicio=servicio)

@app.route('/servicios/<int:servicio_id>/eliminar', methods=['POST'])
@login_required
def eliminar_servicio(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)

    # Verificar si hay proyectos usando este servicio
    proyectos_count = Proyecto.query.filter_by(servicio_id=servicio_id).count()
    if proyectos_count > 0:
        return jsonify({
            'error': f'No se puede eliminar. Hay {proyectos_count} proyecto(s) usando este servicio.'
        }), 400

    db.session.delete(servicio)
    db.session.commit()
    return redirect(url_for('listar_servicios'))

# API endpoints
@app.route('/api/capacidad/<int:meses>')
@login_required
def api_capacidad(meses):
    capacidad = calcular_capacidad_equipo(periodo_meses=meses)
    return jsonify(capacidad)

@app.route('/api/sin-horas')
@login_required
def api_sin_horas():
    sin_horas = personas_sin_horas_recientes()
    return jsonify(sin_horas)

@app.route('/api/necesidad-contratacion', methods=['POST'])
@login_required
def api_necesidad_contratacion():
    data = request.json
    resultado = calcular_necesidad_contratacion(
        data.get('horas_socio', 0),
        data.get('horas_director', 0),
        data.get('horas_consultor', 0),
        data.get('area', None)
    )
    return jsonify(resultado)

@app.route('/api/rentabilidad/cliente/<int:cliente_id>/<int:meses>')
@login_required
def api_rentabilidad_cliente(cliente_id, meses):
    rentabilidad = calcular_rentabilidad_cliente(cliente_id, periodo_meses=meses)
    return jsonify(rentabilidad)

@app.route('/api/rentabilidad/ranking')
@login_required
def api_ranking_rentabilidad():
    year = request.args.get('year', datetime.now().year, type=int)
    top = request.args.get('top', 10, type=int)
    ranking = ranking_clientes_rentables(year=year, top=top)
    return jsonify(ranking)

@app.route('/api/rentabilidad/areas')
@login_required
def api_rentabilidad_areas():
    areas = rentabilidad_por_area()
    return jsonify(areas)

@app.route('/api/pricing', methods=['POST'])
@login_required
def api_pricing():
    data = request.json
    precio = calcular_precio_proyecto(
        data.get('horas_por_cargo', {}),
        data.get('margen_deseado', 12.5)
    )
    return jsonify(precio)

@app.route('/api/productividad/<int:persona_id>/<int:meses>')
@login_required
def api_productividad(persona_id, meses):
    productividad = reporte_productividad_persona(persona_id, periodo_meses=meses)
    return jsonify(productividad)

# ============= API ENDPOINTS PROYECTOS =============

@app.route('/api/proyectos')
@login_required
def api_listar_proyectos():
    """Lista proyectos con filtros opcionales"""
    cliente_id = request.args.get('cliente_id', type=int)
    estado = request.args.get('estado')
    area = request.args.get('area')

    query = Proyecto.query

    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    if estado:
        query = query.filter_by(estado=estado)
    if area:
        query = query.join(Cliente).filter(Cliente.area == area)

    proyectos = query.all()

    resultado = []
    for p in proyectos:
        resultado.append({
            'id': p.id,
            'nombre': p.nombre,
            'codigo': p.codigo,
            'cliente': p.cliente.nombre,
            'cliente_id': p.cliente_id,
            'estado': p.estado,
            'tipo': p.tipo,
            'fecha_inicio': p.fecha_inicio.isoformat() if p.fecha_inicio else None,
            'fecha_fin': p.fecha_fin.isoformat() if p.fecha_fin else None,
            'presupuesto_uf': p.presupuesto_uf,
            'margen_objetivo': p.margen_objetivo
        })

    return jsonify(resultado)

@app.route('/api/proyectos/<int:proyecto_id>')
@login_required
def api_detalle_proyecto(proyecto_id):
    """Detalle completo de un proyecto"""
    proyecto = Proyecto.query.get(proyecto_id)
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404

    # Obtener rentabilidad
    rentabilidad = calcular_rentabilidad_proyecto(proyecto_id)

    # Obtener equipo asignado
    asignaciones = AsignacionProyecto.query.filter_by(proyecto_id=proyecto_id, activo=True).all()
    equipo = [
        {
            'persona_id': a.persona.id,
            'nombre': a.persona.nombre,
            'cargo': a.persona.cargo,
            'rol_proyecto': a.rol_proyecto,
            'horas_estimadas': a.horas_estimadas
        }
        for a in asignaciones
    ]

    return jsonify({
        'proyecto': {
            'id': proyecto.id,
            'nombre': proyecto.nombre,
            'codigo': proyecto.codigo,
            'cliente': proyecto.cliente.nombre,
            'estado': proyecto.estado,
            'descripcion': proyecto.descripcion,
            'fecha_inicio': proyecto.fecha_inicio.isoformat() if proyecto.fecha_inicio else None,
            'fecha_fin': proyecto.fecha_fin.isoformat() if proyecto.fecha_fin else None
        },
        'rentabilidad': rentabilidad,
        'equipo': equipo
    })

@app.route('/api/proyectos', methods=['POST'])
@login_required
def api_crear_proyecto():
    """Crear nuevo proyecto"""
    data = request.json

    try:
        proyecto = Proyecto(
            cliente_id=data['cliente_id'],
            nombre=data['nombre'],
            codigo=data.get('codigo'),
            servicio_id=data.get('servicio_id'),
            tipo=data.get('tipo', 'permanente'),
            fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date() if data.get('fecha_inicio') else None,
            fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date() if data.get('fecha_fin') else None,
            presupuesto_uf=data.get('presupuesto_uf'),
            estado=data.get('estado', 'activo'),
            descripcion=data.get('descripcion', ''),
            margen_objetivo=data.get('margen_objetivo', 12.5)
        )

        db.session.add(proyecto)
        db.session.commit()

        return jsonify({
            'mensaje': 'Proyecto creado exitosamente',
            'proyecto_id': proyecto.id,
            'codigo': proyecto.codigo
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/proyectos/<int:proyecto_id>/rentabilidad')
@login_required
def api_rentabilidad_proyecto(proyecto_id):
    """Rentabilidad de un proyecto"""
    meses = request.args.get('meses', type=int)
    rentabilidad = calcular_rentabilidad_proyecto(proyecto_id, periodo_meses=meses)

    if not rentabilidad:
        return jsonify({'error': 'Proyecto no encontrado'}), 404

    return jsonify(rentabilidad)

@app.route('/api/proyectos/<int:proyecto_id>/asignar', methods=['POST'])
@login_required
def api_asignar_persona_proyecto(proyecto_id):
    """Asignar persona a proyecto"""
    data = request.json

    try:
        asignacion = AsignacionProyecto(
            persona_id=data['persona_id'],
            proyecto_id=proyecto_id,
            rol_proyecto=data.get('rol_proyecto', 'colaborador'),
            horas_estimadas=data.get('horas_estimadas'),
            costo_hora_proyecto=data.get('costo_hora_proyecto'),
            fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date() if data.get('fecha_inicio') else datetime.now().date(),
            activo=True
        )

        db.session.add(asignacion)
        db.session.commit()

        return jsonify({'mensaje': 'Persona asignada exitosamente'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/personas/<int:persona_id>/proyectos')
@login_required
def api_proyectos_persona(persona_id):
    """Proyectos de una persona"""
    proyectos = listar_proyectos_persona(persona_id)
    return jsonify(proyectos)

@app.route('/api/personas/<int:persona_id>/proyectos/<int:proyecto_id>/productividad')
@login_required
def api_productividad_persona_proyecto(persona_id, proyecto_id):
    """Productividad de una persona en un proyecto específico"""
    meses = request.args.get('meses', type=int)
    productividad = reporte_productividad_persona_en_proyecto(persona_id, proyecto_id, periodo_meses=meses)

    if not productividad:
        return jsonify({'error': 'Persona o proyecto no encontrado'}), 404

    return jsonify(productividad)

@app.route('/api/clientes/<int:cliente_id>/proyectos')
@login_required
def api_proyectos_cliente(cliente_id):
    """Proyectos de un cliente"""
    proyectos = listar_proyectos_cliente(cliente_id)
    return jsonify(proyectos)

@app.route('/api/clientes/<int:cliente_id>/proyectos/comparar')
@login_required
def api_comparar_proyectos_cliente(cliente_id):
    """Comparar rentabilidad de proyectos de un cliente"""
    comparacion = comparar_proyectos_cliente(cliente_id)

    if not comparacion:
        return jsonify({'error': 'Cliente no encontrado o sin proyectos'}), 404

    return jsonify(comparacion)

@app.route('/api/proyectos/riesgo')
@login_required
def api_proyectos_riesgo():
    """Proyectos en riesgo"""
    proyectos = proyectos_en_riesgo()
    return jsonify(proyectos)

# Ruta para inicializar datos de ejemplo
@app.route('/inicializar-datos')
@login_required
def inicializar_datos():
    """Crea datos de ejemplo para testing"""
    # Limpiar datos existentes
    db.drop_all()
    db.create_all()
    
    # Crear áreas de servicio
    servicios_data = [
        ('Comunicaciones Externas', 'Externas'),
        ('Gestión de Crisis', 'Externas'),
        ('Talleres de vocería', 'Externas'),
        ('Comunicaciones Internas', 'Internas'),
        ('Asuntos Públicos', 'Asuntos Públicos'),
        ('Estrategia y gestión de redes', 'Redes sociales'),
        ('Monitoreo digital', 'Redes sociales'),
        ('Diseño', 'Diseño'),
    ]
    
    for nombre, area in servicios_data:
        servicio = Servicio(nombre=nombre, area=area)
        db.session.add(servicio)
    
    # Crear personas de ejemplo
    personas_data = [
        ('María González', 'maria@comsulting.cl', 'Socia', 'full-time', 'Externas', 3.5, 150),
        ('Juan Pérez', 'juan@comsulting.cl', 'Director', 'full-time', 'Externas', 2.5, 100),
        ('Ana Martínez', 'ana@comsulting.cl', 'Consultora Senior', 'full-time', 'Externas', 1.8, 70),
        ('Pedro Silva', 'pedro@comsulting.cl', 'Consultor', 'full-time', 'Internas', 1.5, 60),
        ('Carmen López', 'carmen@comsulting.cl', 'Directora', 'full-time', 'Redes sociales', 2.5, 100),
        ('Luis Torres', 'luis@comsulting.cl', 'Designer', 'full-time', 'Diseño', 1.8, 70),
    ]
    
    for nombre, email, cargo, jornada, area, costo, sueldo in personas_data:
        persona = Persona(
            nombre=nombre, email=email, cargo=cargo,
            tipo_jornada=jornada, area=area,
            costo_hora=costo, sueldo_mensual=sueldo
        )
        db.session.add(persona)
    
    # Crear clientes de ejemplo
    clientes_data = [
        ('Cliente A', 'permanente', 'Externas'),
        ('Cliente B', 'permanente', 'Internas'),
        ('Cliente C', 'spot', 'Redes sociales'),
        ('Comsulting', 'permanente', 'Diseño'),
    ]
    
    for nombre, tipo, area in clientes_data:
        cliente = Cliente(
            nombre=nombre, tipo=tipo, area=area,
            fecha_inicio=datetime.now().date() - timedelta(days=365)
        )
        db.session.add(cliente)
    
    db.session.commit()
    
    # Crear horas de ejemplo (últimos 3 meses)
    personas = Persona.query.all()
    clientes = Cliente.query.all()
    
    for persona in personas:
        for i in range(90):  # 90 días
            fecha = datetime.now().date() - timedelta(days=i)
            # Registrar horas aleatorias para diferentes clientes
            horas_dia = 6 + (i % 3)  # Entre 6 y 8 horas
            cliente = clientes[i % len(clientes)]
            
            hora = RegistroHora(
                persona_id=persona.id,
                cliente_id=cliente.id,
                fecha=fecha,
                horas=horas_dia,
                descripcion=f'Trabajo en proyecto {cliente.nombre}'
            )
            db.session.add(hora)
    
    # Crear facturas de ejemplo
    for cliente in clientes:
        for mes in range(3):
            fecha = datetime.now().date() - timedelta(days=30 * mes)
            factura = Factura(
                cliente_id=cliente.id,
                numero=f'F-{cliente.id}-{mes}',
                fecha=fecha,
                monto_uf=100 + (mes * 50),
                pagada=mes > 0
            )
            db.session.add(factura)
    
    # Agregar valor UF actual
    uf = ValorUF(fecha=datetime.now().date(), valor=37500)
    db.session.add(uf)
    
    db.session.commit()
    
    return jsonify({'mensaje': 'Datos inicializados correctamente'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)
