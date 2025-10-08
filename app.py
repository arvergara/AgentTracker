from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
from functools import wraps
import hashlib
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comsulting_simplified.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'comsulting-secret-key-2025-muy-segura-cambiar-en-produccion')

db = SQLAlchemy(app)

# Filtro personalizado para formato latino de números
@app.template_filter('formato_numero')
def formato_numero_filter(valor, decimales=1):
    """Formatea números en formato latino: 1.543,1"""
    try:
        valor = float(valor)
        # Formatear con los decimales especificados
        formato = f"{{:,.{decimales}f}}"
        resultado = formato.format(valor)
        # Cambiar punto por coma para decimales y coma por punto para miles
        resultado = resultado.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
        return resultado
    except (ValueError, TypeError):
        return valor

# ============= CONSTANTES =============
HORAS_EFECTIVAS_MES = 156
VALOR_UF_ACTUAL = 38000  # Actualizar según valor real

def calcular_horas_disponibles_mes(año, mes):
    """
    Calcula las horas disponibles en un mes según días hábiles
    L-J: 9 horas/día
    V: 8 horas/día
    """
    import calendar
    from datetime import date

    # Obtener todos los días del mes
    _, ultimo_dia = calendar.monthrange(año, mes)

    horas_totales = 0
    for dia in range(1, ultimo_dia + 1):
        fecha = date(año, mes, dia)
        dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo

        if dia_semana < 4:  # Lunes a Jueves (0-3)
            horas_totales += 9
        elif dia_semana == 4:  # Viernes (4)
            horas_totales += 8
        # Sábado y Domingo no se cuentan (5-6)

    return horas_totales

# ============= MODELOS SIMPLIFICADOS =============

class Persona(db.Model):
    """Persona que trabaja en Comsulting"""
    __tablename__ = 'personas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(64))  # SHA-256 hash

    # Información laboral
    cargo = db.Column(db.String(50))  # Socio, Director, Consultor Senior, etc.
    es_socia = db.Column(db.Boolean, default=False)  # Solo socias ven info completa
    activo = db.Column(db.Boolean, default=True)
    fecha_ingreso = db.Column(db.Date)

    # Costos (en pesos chilenos)
    costo_mensual_empresa = db.Column(db.Float, nullable=False)  # Costo total mensual empresa

    # Relaciones
    registros_horas = db.relationship('RegistroHora', back_populates='persona', lazy='dynamic')

    @property
    def costo_hora_uf(self):
        """Calcula costo por hora en UF"""
        if self.costo_mensual_empresa <= 0:
            return 0
        costo_hora_pesos = self.costo_mensual_empresa / HORAS_EFECTIVAS_MES
        return round(costo_hora_pesos / VALOR_UF_ACTUAL, 4)

    def verificar_password(self, password):
        """Verifica la contraseña"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def __repr__(self):
        return f'<Persona {self.nombre}>'


class Area(db.Model):
    """Área de trabajo (Externas, Internas, Asuntos Públicos, Redes Sociales, Diseño)"""
    __tablename__ = 'areas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    servicios = db.relationship('Servicio', back_populates='area', lazy='dynamic')
    registros_horas = db.relationship('RegistroHora', back_populates='area', lazy='dynamic')

    def __repr__(self):
        return f'<Area {self.nombre}>'


class Servicio(db.Model):
    """Servicio dentro de un área (Com Externas, Taller de vocería, etc.)"""
    __tablename__ = 'servicios'

    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    area = db.relationship('Area', back_populates='servicios')
    tareas = db.relationship('Tarea', back_populates='servicio', lazy='dynamic')
    registros_horas = db.relationship('RegistroHora', back_populates='servicio', lazy='dynamic')

    def __repr__(self):
        return f'<Servicio {self.nombre}>'


class Tarea(db.Model):
    """Tarea específica dentro de un servicio"""
    __tablename__ = 'tareas'

    id = db.Column(db.Integer, primary_key=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    nombre = db.Column(db.String(500), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    servicio = db.relationship('Servicio', back_populates='tareas')
    registros_horas = db.relationship('RegistroHora', back_populates='tarea', lazy='dynamic')

    def __repr__(self):
        return f'<Tarea {self.nombre}>'


class Cliente(db.Model):
    """Cliente de Comsulting"""
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    tipo = db.Column(db.String(20), default='permanente')  # permanente, spot
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    servicios = db.relationship('ServicioCliente', back_populates='cliente', lazy='dynamic')
    registros_horas = db.relationship('RegistroHora', back_populates='cliente', lazy='dynamic')

    def __repr__(self):
        return f'<Cliente {self.nombre}>'


class ServicioCliente(db.Model):
    """Servicio que un cliente contrata (ej: Asesoría Comunicacional UF 225)"""
    __tablename__ = 'servicios_cliente'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

    nombre = db.Column(db.String(200), nullable=False)  # Ej: "Asesoría Comunicacional"
    valor_mensual_uf = db.Column(db.Float, nullable=False)  # Valor en UF del servicio

    # Para servicios SPOT
    es_spot = db.Column(db.Boolean, default=False)
    fecha_inicio = db.Column(db.Date)  # Para servicios con fecha específica
    fecha_fin = db.Column(db.Date)

    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    cliente = db.relationship('Cliente', back_populates='servicios')
    ingresos_mensuales = db.relationship('IngresoMensual', back_populates='servicio', lazy='dynamic')

    def __repr__(self):
        return f'<ServicioCliente {self.nombre} - {self.valor_mensual_uf} UF>'


class IngresoMensual(db.Model):
    """Registro del ingreso real mensual por servicio (importante para SPOT)"""
    __tablename__ = 'ingresos_mensuales'

    id = db.Column(db.Integer, primary_key=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios_cliente.id'), nullable=False)

    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)  # 1-12
    ingreso_uf = db.Column(db.Float, nullable=False)

    notas = db.Column(db.Text)  # Notas adicionales

    # Relaciones
    servicio = db.relationship('ServicioCliente', back_populates='ingresos_mensuales')

    def __repr__(self):
        return f'<IngresoMensual {self.año}-{self.mes:02d} - {self.ingreso_uf} UF>'


class RegistroHora(db.Model):
    """Registro de horas trabajadas por persona"""
    __tablename__ = 'registros_horas'

    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)

    # Nuevos campos: área, servicio, tarea
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tareas.id'), nullable=False)

    # Campos antiguos (mantener compatibilidad)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    servicio_cliente_id = db.Column(db.Integer, db.ForeignKey('servicios_cliente.id'), nullable=True)

    fecha = db.Column(db.Date, nullable=False)
    horas = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)  # Opcional

    # Relaciones
    persona = db.relationship('Persona', back_populates='registros_horas')
    area = db.relationship('Area', back_populates='registros_horas')
    servicio = db.relationship('Servicio', back_populates='registros_horas')
    tarea = db.relationship('Tarea', back_populates='registros_horas')
    cliente = db.relationship('Cliente', back_populates='registros_horas')
    servicio_cliente = db.relationship('ServicioCliente', backref='registros_horas')

    @property
    def costo_uf(self):
        """Calcula el costo en UF de este registro"""
        return round(self.horas * self.persona.costo_hora_uf, 4)

    def __repr__(self):
        return f'<RegistroHora {self.persona.nombre} - {self.horas}h>'


class Valorizacion(db.Model):
    """Valorización de proyectos y licitaciones"""
    __tablename__ = 'valorizaciones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios_cliente.id'), nullable=True)

    # Datos de la valorización
    horas_totales = db.Column(db.Float, nullable=False)
    costo_directo = db.Column(db.Float, nullable=False)
    overhead_porcentaje = db.Column(db.Float, nullable=False)
    overhead_uf = db.Column(db.Float, nullable=False)
    costo_total = db.Column(db.Float, nullable=False)
    margen_porcentaje = db.Column(db.Float, nullable=False)
    margen_uf = db.Column(db.Float, nullable=False)
    precio_sugerido = db.Column(db.Float, nullable=False)

    # Detalle en JSON
    detalle_recursos = db.Column(db.Text)  # JSON con el detalle

    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    creado_por_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)

    # Relaciones
    cliente = db.relationship('Cliente', backref='valorizaciones')
    servicio = db.relationship('ServicioCliente', backref='valorizaciones')
    creado_por = db.relationship('Persona', backref='valorizaciones')

    def __repr__(self):
        return f'<Valorizacion {self.nombre}>'


# ============= DECORADORES DE AUTENTICACIÓN =============

def login_required(f):
    """Requiere que el usuario esté logueado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def socia_required(f):
    """Requiere que el usuario sea socia"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))

        persona = Persona.query.get(session['user_id'])
        if not persona or not persona.es_socia:
            flash('Acceso denegado. Solo socias pueden ver esta información.', 'error')
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)
    return decorated_function


# ============= RUTAS DE AUTENTICACIÓN =============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        persona = Persona.query.filter_by(email=email, activo=True).first()

        if persona and persona.verificar_password(password):
            session['user_id'] = persona.id
            session['user_name'] = persona.nombre
            session['es_socia'] = persona.es_socia

            flash(f'¡Bienvenida {persona.nombre}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Email o contraseña incorrectos', 'error')

    return render_template('login_simplified.html')


@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))


@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """Cambiar contraseña del usuario actual"""
    persona_id = session.get('user_id')
    persona = Persona.query.get(persona_id)

    if request.method == 'POST':
        password_actual = request.form.get('password_actual')
        password_nueva = request.form.get('password_nueva')
        password_confirmar = request.form.get('password_confirmar')

        # Verificar contraseña actual
        if not persona.verificar_password(password_actual):
            flash('La contraseña actual es incorrecta', 'error')
            return redirect(url_for('cambiar_password'))

        # Verificar que las nuevas contraseñas coincidan
        if password_nueva != password_confirmar:
            flash('Las contraseñas nuevas no coinciden', 'error')
            return redirect(url_for('cambiar_password'))

        # Verificar longitud mínima
        if len(password_nueva) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('cambiar_password'))

        try:
            # Actualizar contraseña
            persona.password_hash = hashlib.sha256(password_nueva.encode()).hexdigest()
            db.session.commit()
            flash('Contraseña actualizada exitosamente', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al cambiar contraseña: {str(e)}', 'error')

    return render_template('cambiar_password.html')


# ============= RUTAS PRINCIPALES =============

@app.route('/')
@login_required
def index():
    """Redirige al dashboard"""
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal - todos pueden ver su información"""
    persona_id = session.get('user_id')
    es_socia = session.get('es_socia', False)

    persona = Persona.query.get(persona_id)

    # Obtener estadísticas personales (todos pueden ver)
    año_actual = datetime.now().year
    mes_actual = datetime.now().month

    # Horas del mes actual
    horas_mes = db.session.query(func.sum(RegistroHora.horas)).filter(
        RegistroHora.persona_id == persona_id,
        extract('year', RegistroHora.fecha) == año_actual,
        extract('month', RegistroHora.fecha) == mes_actual
    ).scalar() or 0

    # Horas del año
    horas_año = db.session.query(func.sum(RegistroHora.horas)).filter(
        RegistroHora.persona_id == persona_id,
        extract('year', RegistroHora.fecha) == año_actual
    ).scalar() or 0

    # Si es socia, mostrar información completa
    stats_empresa = None
    if es_socia:
        # Ingresos totales del mes
        ingresos_mes = db.session.query(func.sum(IngresoMensual.ingreso_uf)).filter(
            IngresoMensual.año == año_actual,
            IngresoMensual.mes == mes_actual
        ).scalar() or 0

        # Costos totales del mes (todas las personas activas)
        personas_activas = Persona.query.filter_by(activo=True).all()
        costo_mensual_total_pesos = sum(p.costo_mensual_empresa for p in personas_activas)
        costo_mensual_total_uf = costo_mensual_total_pesos / VALOR_UF_ACTUAL

        # Margen
        margen_uf = ingresos_mes - costo_mensual_total_uf
        margen_porcentaje = (margen_uf / ingresos_mes * 100) if ingresos_mes > 0 else 0

        stats_empresa = {
            'ingresos_mes': round(ingresos_mes, 2),
            'costos_mes': round(costo_mensual_total_uf, 2),
            'margen_uf': round(margen_uf, 2),
            'margen_porcentaje': round(margen_porcentaje, 2),
            'personal_activo': len(personas_activas)
        }

    return render_template('dashboard_simplified.html',
                          persona=persona,
                          horas_mes=round(horas_mes, 2),
                          horas_año=round(horas_año, 2),
                          stats_empresa=stats_empresa)


@app.route('/registrar-horas', methods=['GET', 'POST'])
@login_required
def registrar_horas():
    """Formulario para registrar horas trabajadas"""
    persona_id = session.get('user_id')

    if request.method == 'POST':
        area_id = request.form.get('area_id', type=int)
        servicio_id = request.form.get('servicio_id', type=int)
        tarea_id = request.form.get('tarea_id', type=int)
        fecha_str = request.form.get('fecha')
        horas = request.form.get('horas', type=float)
        descripcion = request.form.get('descripcion', '').strip()

        # Validar campos obligatorios
        if not all([area_id, servicio_id, tarea_id, fecha_str, horas]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return redirect(url_for('registrar_horas'))

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

            # Validar que la fecha esté dentro de los últimos 7 días
            hoy = datetime.now().date()
            hace_7_dias = hoy - timedelta(days=7)

            if fecha > hoy:
                flash('No puedes registrar horas de fechas futuras', 'error')
                return redirect(url_for('registrar_horas'))

            if fecha < hace_7_dias:
                flash('Solo puedes registrar horas de los últimos 7 días', 'error')
                return redirect(url_for('registrar_horas'))

            registro = RegistroHora(
                persona_id=persona_id,
                area_id=area_id,
                servicio_id=servicio_id,
                tarea_id=tarea_id,
                fecha=fecha,
                horas=horas,
                descripcion=descripcion
            )
            db.session.add(registro)
            db.session.commit()

            flash(f'{horas} horas registradas exitosamente', 'success')
            return redirect(url_for('mis_horas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar horas: {str(e)}', 'error')

    # GET: mostrar formulario
    areas = Area.query.filter_by(activo=True).order_by(Area.nombre).all()
    fecha_hoy = date.today().strftime('%Y-%m-%d')
    return render_template('registrar_horas.html', areas=areas, fecha_hoy=fecha_hoy)


@app.route('/api/cliente/<int:cliente_id>/servicios')
@login_required
def api_servicios_cliente(cliente_id):
    """API para obtener servicios de un cliente (para select dinámico)"""
    servicios = ServicioCliente.query.filter_by(cliente_id=cliente_id, activo=True).all()
    return jsonify([{
        'id': s.id,
        'nombre': s.nombre,
        'valor_uf': s.valor_mensual_uf,
        'es_spot': s.es_spot
    } for s in servicios])


@app.route('/api/area/<int:area_id>/servicios')
@login_required
def api_servicios_por_area(area_id):
    """API para obtener servicios de un área"""
    servicios = Servicio.query.filter_by(area_id=area_id, activo=True).order_by(Servicio.nombre).all()
    return jsonify([{
        'id': s.id,
        'nombre': s.nombre
    } for s in servicios])


@app.route('/api/servicio/<int:servicio_id>/tareas')
@login_required
def api_tareas_por_servicio(servicio_id):
    """API para obtener tareas de un servicio"""
    tareas = Tarea.query.filter_by(servicio_id=servicio_id, activo=True).order_by(Tarea.nombre).all()
    return jsonify([{
        'id': t.id,
        'nombre': t.nombre
    } for t in tareas])


@app.route('/mis-horas')
@login_required
def mis_horas():
    """Ver mis registros de horas"""
    persona_id = session.get('user_id')

    # Filtros opcionales
    año = request.args.get('año', datetime.now().year, type=int)
    mes = request.args.get('mes', type=int)

    query = RegistroHora.query.filter_by(persona_id=persona_id)
    query = query.filter(extract('year', RegistroHora.fecha) == año)

    if mes:
        query = query.filter(extract('month', RegistroHora.fecha) == mes)

    registros = query.order_by(RegistroHora.fecha.desc()).all()

    total_horas = sum(r.horas for r in registros)
    total_costo_uf = sum(r.costo_uf for r in registros)

    return render_template('mis_horas.html',
                          registros=registros,
                          total_horas=round(total_horas, 2),
                          total_costo_uf=round(total_costo_uf, 2),
                          año=año,
                          mes=mes)


@app.route('/horas/<int:registro_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_horas(registro_id):
    """Editar un registro de horas (solo el dueño del registro)"""
    persona_id = session.get('user_id')
    registro = RegistroHora.query.get_or_404(registro_id)

    # Verificar que el usuario sea dueño del registro
    if registro.persona_id != persona_id:
        flash('No tienes permiso para editar este registro', 'error')
        return redirect(url_for('mis_horas'))

    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', type=int)
        servicio_id = request.form.get('servicio_id', type=int)
        fecha_str = request.form.get('fecha')
        horas = request.form.get('horas', type=float)
        descripcion = request.form.get('descripcion', '').strip()

        if not all([cliente_id, servicio_id, fecha_str, horas]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return redirect(url_for('editar_horas', registro_id=registro_id))

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

            registro.cliente_id = cliente_id
            registro.servicio_id = servicio_id
            registro.fecha = fecha
            registro.horas = horas
            registro.descripcion = descripcion

            db.session.commit()
            flash(f'✅ Registro actualizado exitosamente', 'success')
            return redirect(url_for('mis_horas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el registro: {str(e)}', 'error')

    # GET: mostrar formulario con datos actuales
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    servicios = ServicioCliente.query.filter_by(cliente_id=registro.cliente_id, activo=True).all()

    return render_template('editar_horas.html',
                          registro=registro,
                          clientes=clientes,
                          servicios=servicios)


@app.route('/horas/<int:registro_id>/eliminar', methods=['POST'])
@login_required
def eliminar_horas(registro_id):
    """Eliminar un registro de horas (solo el dueño del registro)"""
    persona_id = session.get('user_id')
    registro = RegistroHora.query.get_or_404(registro_id)

    # Verificar que el usuario sea dueño del registro
    if registro.persona_id != persona_id:
        flash('No tienes permiso para eliminar este registro', 'error')
        return redirect(url_for('mis_horas'))

    try:
        db.session.delete(registro)
        db.session.commit()
        flash('✅ Registro eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el registro: {str(e)}', 'error')

    return redirect(url_for('mis_horas'))


@app.route('/clientes')
@socia_required
def ver_clientes():
    """Ver todos los clientes (solo socias)"""
    # Separar clientes permanentes y SPOT
    clientes_permanentes = Cliente.query.filter_by(tipo='permanente', activo=True).order_by(Cliente.nombre).all()
    clientes_spot = Cliente.query.filter_by(tipo='spot', activo=True).order_by(Cliente.nombre).all()

    # Calcular ingresos para clientes permanentes (mensual)
    permanentes_data = []
    total_mensual_permanentes = 0

    for cliente in clientes_permanentes:
        if cliente.nombre == 'CLIENTES PERMANENTES':
            continue
        servicios = cliente.servicios.filter_by(activo=True).all()
        ingreso_mensual = sum(s.valor_mensual_uf for s in servicios)
        total_mensual_permanentes += ingreso_mensual

        permanentes_data.append({
            'cliente': cliente,
            'servicios': servicios,
            'ingreso_mensual': round(ingreso_mensual, 2),
            'num_servicios': len(servicios)
        })

    # Calcular ingresos para clientes SPOT (anual)
    spot_data = []
    total_anual_spot = 0

    for cliente in clientes_spot:
        servicios = cliente.servicios.filter_by(activo=True).all()
        ingreso_anual = sum(s.valor_mensual_uf * 12 for s in servicios)  # Anualizado
        total_anual_spot += ingreso_anual

        spot_data.append({
            'cliente': cliente,
            'servicios': servicios,
            'ingreso_anual': round(ingreso_anual, 2),
            'num_servicios': len(servicios)
        })

    return render_template('clientes.html',
                          permanentes_data=permanentes_data,
                          spot_data=spot_data,
                          total_mensual_permanentes=round(total_mensual_permanentes, 2),
                          total_anual_spot=round(total_anual_spot, 2))


@app.route('/personal')
@socia_required
def ver_personal():
    """Ver todo el personal (solo socias)"""
    personas = Persona.query.order_by(Persona.activo.desc(), Persona.es_socia.desc(), Persona.nombre).all()

    return render_template('personal.html', personas=personas)


@app.route('/personal/nuevo', methods=['GET', 'POST'])
@socia_required
def nuevo_personal():
    """Agregar nueva persona al equipo"""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        cargo = request.form.get('cargo')
        es_socia = request.form.get('es_socia') == 'on'
        costo_mensual = float(request.form.get('costo_mensual', 0))
        fecha_ingreso_str = request.form.get('fecha_ingreso')

        # Verificar que el email no exista
        if Persona.query.filter_by(email=email).first():
            flash('Ya existe una persona con ese email', 'error')
            return redirect(url_for('nuevo_personal'))

        try:
            fecha_ingreso = datetime.strptime(fecha_ingreso_str, '%Y-%m-%d').date() if fecha_ingreso_str else None

            # Generar password por defecto
            import hashlib
            password_hash = hashlib.sha256('comsulting2025'.encode()).hexdigest()

            persona = Persona(
                nombre=nombre,
                email=email,
                password_hash=password_hash,
                cargo=cargo,
                es_socia=es_socia,
                costo_mensual_empresa=costo_mensual,
                activo=True,
                fecha_ingreso=fecha_ingreso
            )
            db.session.add(persona)
            db.session.commit()

            flash(f'Persona {nombre} agregada exitosamente. Password: comsulting2025', 'success')
            return redirect(url_for('ver_personal'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar persona: {str(e)}', 'error')

    return render_template('personal_form.html', persona=None)


@app.route('/personal/<int:persona_id>/editar', methods=['GET', 'POST'])
@socia_required
def editar_personal(persona_id):
    """Editar datos de una persona"""
    persona = Persona.query.get_or_404(persona_id)

    if request.method == 'POST':
        persona.nombre = request.form.get('nombre')
        persona.email = request.form.get('email')
        persona.cargo = request.form.get('cargo')
        persona.es_socia = request.form.get('es_socia') == 'on'
        persona.costo_mensual_empresa = float(request.form.get('costo_mensual', 0))
        persona.activo = request.form.get('activo') == 'on'

        fecha_ingreso_str = request.form.get('fecha_ingreso')
        if fecha_ingreso_str:
            persona.fecha_ingreso = datetime.strptime(fecha_ingreso_str, '%Y-%m-%d').date()

        try:
            db.session.commit()
            flash(f'Datos de {persona.nombre} actualizados exitosamente', 'success')
            return redirect(url_for('ver_personal'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'error')

    return render_template('personal_form.html', persona=persona)


@app.route('/personal/<int:persona_id>/desactivar', methods=['POST'])
@socia_required
def desactivar_personal(persona_id):
    """Desactivar una persona (marcar como inactiva)"""
    persona = Persona.query.get_or_404(persona_id)

    try:
        persona.activo = False
        db.session.commit()
        flash(f'{persona.nombre} marcado como inactivo', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('ver_personal'))


@app.route('/capacidad')
@socia_required
def capacidad():
    """Análisis de capacidad y carga de trabajo del personal"""
    año = request.args.get('año', datetime.now().year, type=int)
    mes = request.args.get('mes', datetime.now().month, type=int)

    # Calcular días hábiles del mes (aproximado: 22 días hábiles al mes)
    DIAS_HABILES_MES = 22
    HORAS_DIA = 8
    HORAS_ESPERADAS_MES = DIAS_HABILES_MES * HORAS_DIA  # 176 horas

    personas_analisis = []
    personas = Persona.query.filter_by(activo=True).order_by(Persona.nombre).all()

    for persona in personas:
        # Obtener registros de horas del mes/año
        registros = RegistroHora.query.filter_by(persona_id=persona.id).filter(
            db.extract('year', RegistroHora.fecha) == año,
            db.extract('month', RegistroHora.fecha) == mes
        ).all()

        total_horas = sum(r.horas for r in registros)
        total_dias_registrados = len(set(r.fecha for r in registros))  # Días únicos con registro

        # Calcular utilización
        utilizacion = (total_horas / HORAS_ESPERADAS_MES * 100) if HORAS_ESPERADAS_MES > 0 else 0

        # Determinar estado
        if utilizacion == 0:
            estado = 'sin_registro'
            estado_texto = 'Sin registros'
        elif utilizacion < 60:
            estado = 'bajo'
            estado_texto = 'Baja utilización'
        elif utilizacion < 90:
            estado = 'optimo'
            estado_texto = 'Óptimo'
        elif utilizacion <= 110:
            estado = 'alto'
            estado_texto = 'Alta utilización'
        else:
            estado = 'sobrecarga'
            estado_texto = 'Sobrecarga'

        # Análisis por cliente
        clientes_trabajados = {}
        for registro in registros:
            cliente_nombre = registro.cliente.nombre
            if cliente_nombre not in clientes_trabajados:
                clientes_trabajados[cliente_nombre] = {
                    'horas': 0,
                    'servicios': set()
                }
            clientes_trabajados[cliente_nombre]['horas'] += registro.horas
            if registro.servicio:
                clientes_trabajados[cliente_nombre]['servicios'].add(registro.servicio.nombre)

        # Convertir a lista ordenada por horas
        clientes_detalle = [
            {
                'nombre': nombre,
                'horas': datos['horas'],
                'servicios': list(datos['servicios']),
                'porcentaje': round(datos['horas'] / total_horas * 100, 1) if total_horas > 0 else 0
            }
            for nombre, datos in clientes_trabajados.items()
        ]
        clientes_detalle.sort(key=lambda x: x['horas'], reverse=True)

        personas_analisis.append({
            'persona': persona,
            'total_horas': round(total_horas, 1),
            'horas_esperadas': HORAS_ESPERADAS_MES,
            'dias_registrados': total_dias_registrados,
            'dias_esperados': DIAS_HABILES_MES,
            'utilizacion': round(utilizacion, 1),
            'estado': estado,
            'estado_texto': estado_texto,
            'clientes': clientes_detalle,
            'num_clientes': len(clientes_trabajados)
        })

    # Ordenar por utilización (los con menos utilización primero, para detectar problemas)
    personas_analisis.sort(key=lambda x: x['utilizacion'])

    # Estadísticas generales
    total_personas = len(personas_analisis)
    con_registro = len([p for p in personas_analisis if p['total_horas'] > 0])
    sin_registro = total_personas - con_registro
    utilizacion_promedio = sum(p['utilizacion'] for p in personas_analisis) / total_personas if total_personas > 0 else 0

    stats = {
        'total_personas': total_personas,
        'con_registro': con_registro,
        'sin_registro': sin_registro,
        'utilizacion_promedio': round(utilizacion_promedio, 1),
        'mes': mes,
        'año': año
    }

    return render_template('capacidad.html',
                          personas_analisis=personas_analisis,
                          stats=stats,
                          año=año,
                          mes=mes)


# ============= GESTIÓN DE CLIENTES Y SERVICIOS =============

@app.route('/cliente/<int:cliente_id>/editar', methods=['GET', 'POST'])
@socia_required
def editar_cliente(cliente_id):
    """Editar cliente y sus servicios"""
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == 'POST':
        cliente.nombre = request.form.get('nombre')
        cliente.tipo = request.form.get('tipo')
        cliente.activo = request.form.get('activo') == 'on'

        db.session.commit()
        flash(f'Cliente {cliente.nombre} actualizado exitosamente', 'success')
        return redirect(url_for('ver_clientes'))

    servicios = cliente.servicios.all()
    return render_template('editar_cliente.html', cliente=cliente, servicios=servicios)


@app.route('/cliente/<int:cliente_id>/servicio/nuevo', methods=['GET', 'POST'])
@socia_required
def nuevo_servicio(cliente_id):
    """Agregar nuevo servicio a un cliente"""
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        valor_mensual_uf = float(request.form.get('valor_mensual_uf'))
        es_spot = request.form.get('es_spot') == 'on'

        # Capturar fechas si es SPOT
        fecha_inicio = None
        fecha_fin = None
        if es_spot:
            fecha_inicio_str = request.form.get('fecha_inicio')
            fecha_fin_str = request.form.get('fecha_fin')
            if fecha_inicio_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            if fecha_fin_str:
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

        servicio = ServicioCliente(
            cliente_id=cliente.id,
            nombre=nombre,
            valor_mensual_uf=valor_mensual_uf,
            es_spot=es_spot,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            activo=True
        )
        db.session.add(servicio)
        db.session.commit()

        # Crear ingresos mensuales
        if not es_spot:
            # Servicio permanente: crear para todo el año actual
            año_actual = datetime.now().year
            for mes in range(1, 13):
                ingreso = IngresoMensual(
                    servicio_id=servicio.id,
                    año=año_actual,
                    mes=mes,
                    ingreso_uf=valor_mensual_uf
                )
                db.session.add(ingreso)
        else:
            # Servicio spot: crear solo para el rango de fechas
            if fecha_inicio and fecha_fin:
                año_inicio = fecha_inicio.year
                año_fin = fecha_fin.year
                mes_inicio = fecha_inicio.month
                mes_fin = fecha_fin.month

                for año in range(año_inicio, año_fin + 1):
                    mes_start = mes_inicio if año == año_inicio else 1
                    mes_end = mes_fin if año == año_fin else 12

                    for mes in range(mes_start, mes_end + 1):
                        ingreso = IngresoMensual(
                            servicio_id=servicio.id,
                            año=año,
                            mes=mes,
                            ingreso_uf=valor_mensual_uf
                        )
                        db.session.add(ingreso)

        db.session.commit()

        flash(f'Servicio {nombre} agregado exitosamente', 'success')
        return redirect(url_for('editar_cliente', cliente_id=cliente.id))

    return render_template('nuevo_servicio.html', cliente=cliente)


@app.route('/servicio/<int:servicio_id>/editar', methods=['GET', 'POST'])
@socia_required
def editar_servicio(servicio_id):
    """Editar un servicio existente"""
    servicio = ServicioCliente.query.get_or_404(servicio_id)

    if request.method == 'POST':
        servicio.nombre = request.form.get('nombre')
        nuevo_valor = float(request.form.get('valor_mensual_uf'))
        servicio.es_spot = request.form.get('es_spot') == 'on'
        servicio.activo = request.form.get('activo') == 'on'

        # Capturar fechas si es SPOT
        if servicio.es_spot:
            fecha_inicio_str = request.form.get('fecha_inicio')
            fecha_fin_str = request.form.get('fecha_fin')
            if fecha_inicio_str:
                servicio.fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            if fecha_fin_str:
                servicio.fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

        # Si cambió el valor y no es SPOT, actualizar ingresos mensuales
        if nuevo_valor != servicio.valor_mensual_uf and not servicio.es_spot:
            servicio.valor_mensual_uf = nuevo_valor
            # Actualizar ingresos mensuales existentes
            IngresoMensual.query.filter_by(servicio_id=servicio.id).update(
                {'ingreso_uf': nuevo_valor}
            )
        else:
            servicio.valor_mensual_uf = nuevo_valor

        db.session.commit()
        flash(f'Servicio actualizado exitosamente', 'success')
        return redirect(url_for('editar_cliente', cliente_id=servicio.cliente_id))

    return render_template('editar_servicio.html', servicio=servicio)


@app.route('/servicio/<int:servicio_id>/eliminar', methods=['POST'])
@socia_required
def eliminar_servicio(servicio_id):
    """Eliminar un servicio"""
    servicio = ServicioCliente.query.get_or_404(servicio_id)
    cliente_id = servicio.cliente_id

    # Eliminar ingresos mensuales asociados
    IngresoMensual.query.filter_by(servicio_id=servicio.id).delete()

    db.session.delete(servicio)
    db.session.commit()

    flash('Servicio eliminado exitosamente', 'success')
    return redirect(url_for('editar_cliente', cliente_id=cliente_id))


@app.route('/cliente/nuevo', methods=['GET', 'POST'])
@socia_required
def nuevo_cliente():
    """Crear nuevo cliente"""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo = request.form.get('tipo', 'permanente')

        cliente = Cliente(
            nombre=nombre,
            tipo=tipo,
            activo=True
        )
        db.session.add(cliente)
        db.session.commit()

        flash(f'Cliente {nombre} creado exitosamente', 'success')
        return redirect(url_for('editar_cliente', cliente_id=cliente.id))

    return render_template('nuevo_cliente.html')


@app.route('/rentabilidad')
@socia_required
def rentabilidad():
    """Análisis de rentabilidad por cliente y servicio (solo socias)"""
    año = request.args.get('año', datetime.now().year, type=int)
    mes = request.args.get('mes', type=int)

    # Ingresos mensuales
    query_ingresos = IngresoMensual.query.filter_by(año=año)
    if mes:
        query_ingresos = query_ingresos.filter_by(mes=mes)

    ingresos = query_ingresos.all()
    total_ingresos = sum(i.ingreso_uf for i in ingresos)

    # Costos mensuales (todas las personas activas)
    personas_activas = Persona.query.filter_by(activo=True).all()
    costo_total_pesos = sum(p.costo_mensual_empresa for p in personas_activas)
    costo_total_uf = costo_total_pesos / VALOR_UF_ACTUAL

    # Si es un mes específico, usar ese costo
    if mes:
        costos_mes = costo_total_uf
    else:
        # Si es el año completo, multiplicar por 12
        costos_mes = costo_total_uf * 12

    # Margen
    margen_uf = total_ingresos - costos_mes
    margen_porcentaje = (margen_uf / total_ingresos * 100) if total_ingresos > 0 else 0

    stats = {
        'total_ingresos': round(total_ingresos, 2),
        'total_costos': round(costos_mes, 2),
        'margen_uf': round(margen_uf, 2),
        'margen_porcentaje': round(margen_porcentaje, 2),
        'personal_activo': len(personas_activas)
    }

    # ===== CALCULAR HORAS NO IMPUTADAS (para COMSULTING) =====
    cliente_comsulting = Cliente.query.filter_by(nombre='COMSULTING').first()
    horas_no_imputadas_total = 0
    costo_no_imputadas_total = 0

    if mes:
        # Calcular para un mes específico
        horas_disponibles_mes = calcular_horas_disponibles_mes(año, mes)

        for persona in personas_activas:
            # Horas registradas por esta persona en el mes
            horas_registradas = db.session.query(func.sum(RegistroHora.horas)).filter(
                RegistroHora.persona_id == persona.id,
                extract('year', RegistroHora.fecha) == año,
                extract('month', RegistroHora.fecha) == mes
            ).scalar() or 0

            # Horas no imputadas = disponibles - registradas
            horas_gap = max(0, horas_disponibles_mes - horas_registradas)

            if horas_gap > 0:
                horas_no_imputadas_total += horas_gap
                costo_no_imputadas_total += horas_gap * persona.costo_hora_uf
    else:
        # Para el año completo, calcular mes por mes
        for mes_iter in range(1, 13):
            horas_disponibles_mes = calcular_horas_disponibles_mes(año, mes_iter)

            for persona in personas_activas:
                horas_registradas = db.session.query(func.sum(RegistroHora.horas)).filter(
                    RegistroHora.persona_id == persona.id,
                    extract('year', RegistroHora.fecha) == año,
                    extract('month', RegistroHora.fecha) == mes_iter
                ).scalar() or 0

                horas_gap = max(0, horas_disponibles_mes - horas_registradas)

                if horas_gap > 0:
                    horas_no_imputadas_total += horas_gap
                    costo_no_imputadas_total += horas_gap * persona.costo_hora_uf

    # ===== ANÁLISIS POR CLIENTE =====
    clientes_analisis = []
    clientes = Cliente.query.filter_by(activo=True).all()

    for cliente in clientes:
        if cliente.nombre == 'CLIENTES PERMANENTES':
            continue

        # Calcular ingresos del cliente
        ingresos_cliente = IngresoMensual.query.join(ServicioCliente).filter(
            ServicioCliente.cliente_id == cliente.id,
            IngresoMensual.año == año
        )
        if mes:
            ingresos_cliente = ingresos_cliente.filter(IngresoMensual.mes == mes)

        ingresos_cliente = ingresos_cliente.all()
        total_ingresos_cliente = sum(i.ingreso_uf for i in ingresos_cliente)

        # Calcular costos (horas trabajadas en este cliente)
        registros_horas = RegistroHora.query.filter_by(cliente_id=cliente.id).filter(
            db.extract('year', RegistroHora.fecha) == año
        )
        if mes:
            registros_horas = registros_horas.filter(db.extract('month', RegistroHora.fecha) == mes)

        registros_horas = registros_horas.all()
        total_horas_cliente = sum(r.horas for r in registros_horas)
        total_costos_cliente = sum(r.costo_uf for r in registros_horas)

        # Calcular margen
        margen_cliente = total_ingresos_cliente - total_costos_cliente
        margen_porcentaje_cliente = (margen_cliente / total_ingresos_cliente * 100) if total_ingresos_cliente > 0 else 0

        # Análisis por servicio
        servicios_analisis = []
        for servicio in cliente.servicios.filter_by(activo=True).all():
            # Ingresos del servicio
            ingresos_servicio = IngresoMensual.query.filter_by(
                servicio_id=servicio.id,
                año=año
            )
            if mes:
                ingresos_servicio = ingresos_servicio.filter_by(mes=mes)

            ingresos_servicio = ingresos_servicio.all()
            total_ingresos_servicio = sum(i.ingreso_uf for i in ingresos_servicio)

            # Costos del servicio (horas trabajadas en este servicio)
            registros_servicio = RegistroHora.query.filter_by(servicio_id=servicio.id).filter(
                db.extract('year', RegistroHora.fecha) == año
            )
            if mes:
                registros_servicio = registros_servicio.filter(db.extract('month', RegistroHora.fecha) == mes)

            registros_servicio = registros_servicio.all()
            total_horas_servicio = sum(r.horas for r in registros_servicio)
            total_costos_servicio = sum(r.costo_uf for r in registros_servicio)

            margen_servicio = total_ingresos_servicio - total_costos_servicio
            margen_porcentaje_servicio = (margen_servicio / total_ingresos_servicio * 100) if total_ingresos_servicio > 0 else 0

            if total_ingresos_servicio > 0 or total_costos_servicio > 0:
                servicios_analisis.append({
                    'servicio': servicio,
                    'ingresos': round(total_ingresos_servicio, 2),
                    'horas': round(total_horas_servicio, 2),
                    'costos': round(total_costos_servicio, 2),
                    'margen': round(margen_servicio, 2),
                    'margen_porcentaje': round(margen_porcentaje_servicio, 2)
                })

        # Incluir cliente si tiene ingresos, costos, o es COMSULTING (siempre mostrar)
        if total_ingresos_cliente > 0 or total_costos_cliente > 0 or cliente.nombre == 'COMSULTING':
            # Si es COMSULTING, agregar las horas no imputadas
            if cliente.nombre == 'COMSULTING':
                horas_imputadas = total_horas_cliente
                costos_imputados = total_costos_cliente

                # Sumar horas no imputadas (gap)
                total_horas_cliente += horas_no_imputadas_total
                total_costos_cliente += costo_no_imputadas_total
                margen_cliente = total_ingresos_cliente - total_costos_cliente

                # Agregar desglose en servicios
                servicios_analisis.insert(0, {
                    'servicio': type('obj', (object,), {'nombre': '📊 HORAS NO IMPUTADAS (Gap)'})(),
                    'ingresos': 0,
                    'horas': round(horas_no_imputadas_total, 2),
                    'costos': round(costo_no_imputadas_total, 2),
                    'margen': round(-costo_no_imputadas_total, 2),
                    'margen_porcentaje': 0,
                    'es_gap': True
                })

                if horas_imputadas > 0:
                    servicios_analisis.insert(1, {
                        'servicio': type('obj', (object,), {'nombre': '✏️ HORAS IMPUTADAS (Registradas)'})(),
                        'ingresos': 0,
                        'horas': round(horas_imputadas, 2),
                        'costos': round(costos_imputados, 2),
                        'margen': round(-costos_imputados, 2),
                        'margen_porcentaje': 0,
                        'es_gap': False
                    })

            clientes_analisis.append({
                'cliente': cliente,
                'ingresos': round(total_ingresos_cliente, 2),
                'horas': round(total_horas_cliente, 2),
                'costos': round(total_costos_cliente, 2),
                'margen': round(margen_cliente, 2),
                'margen_porcentaje': round(margen_porcentaje_cliente, 2) if total_ingresos_cliente > 0 else 0,
                'servicios': servicios_analisis,
                'es_comsulting': cliente.nombre == 'COMSULTING'
            })

    # Ordenar: COMSULTING al final, resto por margen descendente
    clientes_analisis.sort(key=lambda x: (x['es_comsulting'], -x['margen']))

    return render_template('rentabilidad.html',
                          stats=stats,
                          clientes_analisis=clientes_analisis,
                          año=año,
                          mes=mes)


# ============= VALORIZACIÓN DE PROYECTOS =============

@app.route('/valorizacion')
@socia_required
def valorizacion():
    """Calculadora de valorización de proyectos y licitaciones"""
    personas = Persona.query.filter_by(activo=True).all()
    clientes = Cliente.query.filter_by(activo=True).all()

    # Calcular datos para cada persona
    personas_data = []
    for persona in personas:
        personas_data.append({
            'id': persona.id,
            'nombre': persona.nombre,
            'cargo': persona.cargo,
            'costo_uf_hora': persona.costo_hora_uf
        })

    # Datos de clientes
    clientes_data = []
    for cliente in clientes:
        clientes_data.append({
            'id': cliente.id,
            'nombre': cliente.nombre
        })

    # Obtener TODOS los servicios para mostrar nombres existentes
    servicios_existentes = db.session.query(
        ServicioCliente.nombre,
        db.func.count(ServicioCliente.id).label('count')
    ).group_by(ServicioCliente.nombre).all()

    servicios_nombres = [{'nombre': s.nombre, 'count': s.count} for s in servicios_existentes]

    # Obtener valorizaciones guardadas
    valorizaciones = Valorizacion.query.order_by(Valorizacion.fecha_creacion.desc()).limit(10).all()

    return render_template('valorizacion.html',
                          personas=personas_data,
                          clientes=clientes_data,
                          servicios_nombres=servicios_nombres,
                          valorizaciones=valorizaciones)


@app.route('/api/calcular-valorizacion', methods=['POST'])
@socia_required
def calcular_valorizacion():
    """API para calcular valorización de un proyecto"""
    data = request.get_json()

    # Datos recibidos
    recursos = data.get('recursos', [])  # [{ persona_id, horas }]
    overhead_porcentaje = float(data.get('overhead', 30))  # Default 30%
    margen_porcentaje = float(data.get('margen', 20))  # Default 20%

    # Calcular costos
    costo_directo = 0
    detalle_recursos = []

    for recurso in recursos:
        persona = Persona.query.get(recurso['persona_id'])
        if persona:
            horas = float(recurso['horas'])
            tipo_horas = recurso.get('tipo_horas', 'recurrente')  # 'spot' o 'recurrente'
            costo_uf_hora = persona.costo_hora_uf
            costo_persona = horas * costo_uf_hora

            costo_directo += costo_persona

            detalle_recursos.append({
                'nombre': persona.nombre,
                'cargo': persona.cargo,
                'horas': horas,
                'tipo_horas': tipo_horas,
                'costo_uf_hora': round(costo_uf_hora, 4),
                'costo_total': round(costo_persona, 2)
            })

    # Cálculos
    overhead_uf = costo_directo * (overhead_porcentaje / 100)
    costo_total = costo_directo + overhead_uf
    margen_uf = costo_total * (margen_porcentaje / 100)
    precio_sugerido = costo_total + margen_uf

    # Horas totales
    horas_totales = sum(float(r['horas']) for r in recursos)

    return jsonify({
        'detalle_recursos': detalle_recursos,
        'horas_totales': round(horas_totales, 1),
        'costo_directo': round(costo_directo, 2),
        'overhead_porcentaje': overhead_porcentaje,
        'overhead_uf': round(overhead_uf, 2),
        'costo_total': round(costo_total, 2),
        'margen_porcentaje': margen_porcentaje,
        'margen_uf': round(margen_uf, 2),
        'precio_sugerido': round(precio_sugerido, 2)
    })


@app.route('/api/guardar-valorizacion', methods=['POST'])
@socia_required
def guardar_valorizacion():
    """Guarda una valorización y opcionalmente crea cliente/servicio"""
    persona_id = session.get('user_id')
    data = request.get_json()

    try:
        import json as json_lib

        cliente_id = None
        servicio_id = None
        nuevo_cliente = False
        nuevo_servicio = False

        # Manejar cliente
        if data.get('cliente'):
            cliente_data = data['cliente']
            if cliente_data.get('nuevo'):
                # Crear nuevo cliente
                cliente = Cliente(
                    nombre=cliente_data['nombre'],
                    tipo=cliente_data['tipo'],
                    activo=True
                )
                db.session.add(cliente)
                db.session.flush()  # Para obtener el ID
                cliente_id = cliente.id
                nuevo_cliente = True
            else:
                cliente_id = cliente_data.get('id')

        # Manejar servicio
        if data.get('servicio'):
            servicio_data = data['servicio']
            if servicio_data.get('nuevo'):
                if not cliente_id:
                    raise Exception('Se requiere un cliente para crear un servicio')

                # Crear nuevo servicio
                servicio = ServicioCliente(
                    cliente_id=cliente_id,
                    nombre=servicio_data['nombre'],
                    valor_mensual_uf=servicio_data['valor_uf'],
                    es_spot=servicio_data.get('es_spot', False),
                    activo=True
                )
                db.session.add(servicio)
                db.session.flush()  # Para obtener el ID
                servicio_id = servicio.id
                nuevo_servicio = True
            else:
                servicio_id = servicio_data.get('id')

        # Crear valorización
        valorizacion = Valorizacion(
            nombre=data['nombre'],
            cliente_id=cliente_id,
            servicio_id=servicio_id,
            horas_totales=data['horas_totales'],
            costo_directo=data['costo_directo'],
            overhead_porcentaje=data['overhead_porcentaje'],
            overhead_uf=data['overhead_uf'],
            costo_total=data['costo_total'],
            margen_porcentaje=data['margen_porcentaje'],
            margen_uf=data['margen_uf'],
            precio_sugerido=data['precio_sugerido'],
            detalle_recursos=json_lib.dumps(data['detalle_recursos']),
            creado_por_id=persona_id
        )

        db.session.add(valorizacion)
        db.session.commit()

        return jsonify({
            'success': True,
            'id': valorizacion.id,
            'nuevo_cliente': nuevo_cliente,
            'nuevo_servicio': nuevo_servicio
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ============= INICIALIZACIÓN =============

def crear_base_datos():
    """Crea las tablas de la base de datos"""
    with app.app_context():
        db.create_all()
        print("✅ Base de datos creada exitosamente")


if __name__ == '__main__':
    # Crear base de datos si no existe
    if not os.path.exists('comsulting_simplified.db'):
        crear_base_datos()

    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
