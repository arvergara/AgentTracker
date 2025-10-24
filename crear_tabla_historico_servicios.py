#!/usr/bin/env python3
"""
Crear tabla historico_servicios para registrar cambios en valores de servicios
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def cargar_env_produccion():
    env_file = '.env.production'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key == 'DATABASE_URL':
                        os.environ['DATABASE_URL'] = value
                        return True
    return False


def conectar_produccion():
    cargar_env_produccion()
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ No se encontró DATABASE_URL")
        return None, None

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.execute(text('SELECT 1'))
        print("✓ Conectado a base de datos de producción")
        return session, engine
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None, None


def main():
    ejecutar = '--ejecutar' in sys.argv

    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  CREAR TABLA: historico_servicios".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    session, engine = conectar_produccion()

    if not session:
        sys.exit(1)

    # Verificar si la tabla ya existe
    print("Verificando si la tabla historico_servicios ya existe...")
    print("-" * 80)

    result = session.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'historico_servicios'
        )
    """))

    tabla_existe = result.scalar()

    if tabla_existe:
        print("⚠️  La tabla historico_servicios ya existe en la base de datos")
        print("\nNo es necesario ejecutar esta migración")
        return

    print("✓ La tabla no existe, se procederá a crearla")

    if not ejecutar:
        print("\n" + "=" * 80)
        print("⚠️  MODO SIMULACIÓN - No se realizarán cambios")
        print("=" * 80)
        print()
        print("SQL que se ejecutará:")
        print("-" * 80)
        print("""
CREATE TABLE historico_servicios (
    id SERIAL PRIMARY KEY,
    servicio_cliente_id INTEGER REFERENCES servicios_cliente(id) NOT NULL,
    valor_anterior_uf FLOAT NOT NULL,
    valor_nuevo_uf FLOAT NOT NULL,
    fecha_cambio DATE NOT NULL,
    usuario_id INTEGER REFERENCES personas(id),
    motivo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_historico_servicios_servicio_id
    ON historico_servicios(servicio_cliente_id);

CREATE INDEX idx_historico_servicios_fecha_cambio
    ON historico_servicios(fecha_cambio);
        """)
        print("-" * 80)
        print()
        print("Para aplicar estos cambios, ejecuta:")
        print("  python crear_tabla_historico_servicios.py --ejecutar")
        print()
        return

    # Confirmar
    print("\n" + "=" * 80)
    print("⚠️  ADVERTENCIA: Vas a crear una tabla en PRODUCCIÓN")
    print("=" * 80)
    print()
    print("Se creará la tabla: historico_servicios")
    print("Con los siguientes campos:")
    print("  - id (SERIAL PRIMARY KEY)")
    print("  - servicio_cliente_id (INTEGER REFERENCES servicios_cliente)")
    print("  - valor_anterior_uf (FLOAT)")
    print("  - valor_nuevo_uf (FLOAT)")
    print("  - fecha_cambio (DATE)")
    print("  - usuario_id (INTEGER REFERENCES personas)")
    print("  - motivo (TEXT)")
    print("  - created_at (TIMESTAMP)")
    print()
    respuesta = input("¿Continuar? (escribe 'SI' para confirmar): ")

    if respuesta.strip().upper() != 'SI':
        print("\nOperación cancelada")
        return

    # Ejecutar
    print("\nCreando tabla...")
    print("-" * 80)

    with engine.connect() as conn:
        try:
            # Crear tabla
            conn.execute(text("""
                CREATE TABLE historico_servicios (
                    id SERIAL PRIMARY KEY,
                    servicio_cliente_id INTEGER REFERENCES servicios_cliente(id) NOT NULL,
                    valor_anterior_uf FLOAT NOT NULL,
                    valor_nuevo_uf FLOAT NOT NULL,
                    fecha_cambio DATE NOT NULL,
                    usuario_id INTEGER REFERENCES personas(id),
                    motivo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✓ Tabla historico_servicios creada")

            # Crear índices
            conn.execute(text("""
                CREATE INDEX idx_historico_servicios_servicio_id
                    ON historico_servicios(servicio_cliente_id)
            """))
            print("✓ Índice creado en servicio_cliente_id")

            conn.execute(text("""
                CREATE INDEX idx_historico_servicios_fecha_cambio
                    ON historico_servicios(fecha_cambio)
            """))
            print("✓ Índice creado en fecha_cambio")

            conn.commit()

            print()
            print("=" * 80)
            print("✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            print()
            print("La tabla historico_servicios ha sido creada.")
            print("Ahora puedes registrar cambios históricos en los valores de servicios.")
            print()

        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()

    session.close()


if __name__ == '__main__':
    main()
