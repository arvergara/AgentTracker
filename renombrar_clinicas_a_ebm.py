"""
Script para fusionar CLÍNICAS con EBM en la base de datos
- CLÍNICAS (ID: 2) tiene las horas
- EBM (ID: 25) tiene los ingresos
Solución: Mover todos los ingresos de EBM a CLÍNICAS, luego renombrar CLÍNICAS a EBM
"""

from app import app, db, Cliente, ServicioCliente, IngresoMensual, RegistroHora
from sqlalchemy import func
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://agenttracker_db_user:SVoi2QQ0qt0Zye0QPzEj7g2lX9RJ2ANb@dpg-d3pb2i3ipnbc739ps5r0-a.oregon-postgres.render.com/agenttracker_db')

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

with app.app_context():
    # Buscar ambos clientes
    clinicas = Cliente.query.filter_by(nombre='CLÍNICAS').first()
    ebm = Cliente.query.filter_by(nombre='EBM').first()

    if not clinicas:
        print("❌ No se encontró el cliente 'CLÍNICAS'")
        exit(1)

    if not ebm:
        print("❌ No se encontró el cliente 'EBM'")
        exit(1)

    print(f"✅ CLÍNICAS encontrado (ID: {clinicas.id})")
    print(f"✅ EBM encontrado (ID: {ebm.id})")

    # Verificar datos antes de fusionar
    horas_clinicas = db.session.query(func.sum(RegistroHora.horas)).filter(
        RegistroHora.cliente_id == clinicas.id
    ).scalar() or 0

    horas_ebm = db.session.query(func.sum(RegistroHora.horas)).filter(
        RegistroHora.cliente_id == ebm.id
    ).scalar() or 0

    servicios_ebm = ServicioCliente.query.filter_by(cliente_id=ebm.id).count()

    print(f"\n📊 Antes de fusionar:")
    print(f"   CLÍNICAS: {horas_clinicas} horas registradas")
    print(f"   EBM: {horas_ebm} horas registradas, {servicios_ebm} servicios")

    # Paso 1: Mover todos los servicios de EBM a CLÍNICAS
    servicios = ServicioCliente.query.filter_by(cliente_id=ebm.id).all()
    for servicio in servicios:
        print(f"   Moviendo servicio '{servicio.nombre}' de EBM a CLÍNICAS")
        servicio.cliente_id = clinicas.id

    # Paso 2: Mover todos los registros de horas de EBM a CLÍNICAS (si los hay)
    registros = RegistroHora.query.filter_by(cliente_id=ebm.id).all()
    for registro in registros:
        registro.cliente_id = clinicas.id

    # Paso 3: Renombrar el EBM antiguo temporalmente para liberar el nombre
    ebm.nombre = 'EBM_OLD_DEPRECATED'
    ebm.activo = False

    db.session.commit()

    # Paso 4: Renombrar CLÍNICAS a EBM
    clinicas.nombre = 'EBM'

    db.session.commit()

    print(f"\n✅ Fusión completada exitosamente!")
    print(f"   - Servicios e ingresos movidos de EBM (ID: {ebm.id}) a CLÍNICAS (ID: {clinicas.id})")
    print(f"   - Cliente CLÍNICAS renombrado a: EBM")
    print(f"   - Cliente EBM antiguo (ID: {ebm.id}) desactivado")
    print(f"\n🎯 Ahora todas las horas e ingresos están bajo el cliente 'EBM' (ID: {clinicas.id})")
