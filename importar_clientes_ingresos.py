"""
Script para importar clientes, servicios e ingresos desde Cliente_Comsulting.csv
"""
from app import app, db, Cliente, ServicioCliente, IngresoMensual
from datetime import datetime

def importar_clientes_e_ingresos():
    """Importa clientes, sus servicios e ingresos mensuales"""

    with app.app_context():
        print("Importando clientes y servicios...")

        # Limpiar datos existentes
        IngresoMensual.query.delete()
        ServicioCliente.query.delete()
        Cliente.query.delete()
        db.session.commit()

        año_actual = datetime.now().year

        # CLIENTES PERMANENTES
        clientes_permanentes = [
            {
                'nombre': 'AFP MODELO',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Asesoría Comunicacional', 'valor_uf': 225, 'es_spot': False}
                ]
            },
            {
                'nombre': 'EBM',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Asesoría Comunicacional', 'valor_uf': 856, 'es_spot': False},
                    {'nombre': 'Digital', 'valor_uf': 210, 'es_spot': False},
                    {'nombre': 'Isapres', 'valor_uf': 55, 'es_spot': False},
                    {'nombre': 'Monitoreo Sindicatos', 'valor_uf': 14, 'es_spot': False},
                    {'nombre': 'Talleres de vocería promedio mensual', 'valor_uf': 13.2, 'es_spot': False},
                    {'nombre': 'News Letter Clínica Ciudad del Mar', 'valor_uf': 9, 'es_spot': False}
                ]
            },
            {
                'nombre': 'COLLAHUASI',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Asesoría Comunicacional', 'valor_uf': 350, 'es_spot': False},
                    {'nombre': 'Digital gestión RRSS', 'valor_uf': 160, 'es_spot': False},
                    {'nombre': 'Digital monitoreo UF', 'valor_uf': 130, 'es_spot': False},
                    {'nombre': 'Instagram JG', 'valor_uf': 50, 'es_spot': False},
                    {'nombre': 'Diseño', 'valor_uf': 48, 'es_spot': False},
                    {'nombre': 'Extras Diseño promedio mensual', 'valor_uf': 65, 'es_spot': False}
                ]
            },
            {
                'nombre': 'Empresas COPEC',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Comunicaciones corporativas', 'valor_uf': 250, 'es_spot': False}
                ]
            },
            {
                'nombre': 'FALABELLA S.A.',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Asesoría Comunicacional', 'valor_uf': 510, 'es_spot': False},
                    {'nombre': 'Servicio de Diseño', 'valor_uf': 100, 'es_spot': False}
                ]
            },
            {
                'nombre': 'FRUTAS DE CHILE',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Comunicaciones externas y RR.SS', 'valor_uf': 376, 'es_spot': False},
                    {'nombre': 'Asuntos Públicos', 'valor_uf': 100, 'es_spot': False}
                ]
            },
            {
                'nombre': 'GUACOLDA',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Asesoría Comunicacional', 'valor_uf': 150, 'es_spot': False},
                    {'nombre': 'Comunicaciones internas', 'valor_uf': 80, 'es_spot': False},
                    {'nombre': 'Diseño gráfico', 'valor_uf': 44, 'es_spot': False},
                    {'nombre': 'Diseño memoria promedio mensual', 'valor_uf': 18.3, 'es_spot': False}
                ]
            },
            {
                'nombre': 'HITES',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Asesoría Comunicacional', 'valor_uf': 150, 'es_spot': False}
                ]
            },
            {
                'nombre': 'ISIDORO QUIROGA',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Asesoría Comunicacional', 'valor_uf': 150, 'es_spot': False},
                    {'nombre': 'Horas extras promedio mensual', 'valor_uf': 104, 'es_spot': False}
                ]
            },
            {
                'nombre': 'LARRAÍN VIAL',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Monitoreo de noticias diario', 'valor_uf': 30, 'es_spot': False}
                ]
            },
            {
                'nombre': 'LIBERTY SEGUROS',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Monitoreo de noticias diario', 'valor_uf': 30, 'es_spot': False}
                ]
            },
            {
                'nombre': 'MAE HOLDING CHILE SPA',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Asesoría Comunicacional (high intensity)', 'valor_uf': 120, 'es_spot': False},
                    {'nombre': 'Monitoreo Digital', 'valor_uf': 15, 'es_spot': False},
                    {'nombre': 'RRSS', 'valor_uf': 30, 'es_spot': False},
                    {'nombre': 'Extras diseño promedio mensual', 'valor_uf': 4.5, 'es_spot': False}
                ]
            },
            {
                'nombre': 'MANTOS COPPER SA',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Comunicaciones Externas y Gestión de Crisis', 'valor_uf': 100, 'es_spot': False},
                    {'nombre': 'Redes Sociales (Linkedin)', 'valor_uf': 20, 'es_spot': False},
                    {'nombre': 'Comunicaciones Internas y Diseño', 'valor_uf': 107.5, 'es_spot': False},
                    {'nombre': 'Monitoreo RRSS y Medios Digitales', 'valor_uf': 15, 'es_spot': False},
                    {'nombre': 'Asuntos Públicos', 'valor_uf': 35, 'es_spot': False},
                    {'nombre': 'Instagram Capstone Copper Chile', 'valor_uf': 37.5, 'es_spot': False}
                ]
            },
            {
                'nombre': 'MANTO VERDE SA',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Comunicaciones Externas y Gestión de Crisis', 'valor_uf': 100, 'es_spot': False},
                    {'nombre': 'Redes Sociales (Linkedin)', 'valor_uf': 20, 'es_spot': False},
                    {'nombre': 'Comunicaciones Internas y Diseño', 'valor_uf': 107.5, 'es_spot': False},
                    {'nombre': 'Monitoreo RRSS y Medios Digitales', 'valor_uf': 15, 'es_spot': False},
                    {'nombre': 'Asuntos Públicos', 'valor_uf': 35, 'es_spot': False},
                    {'nombre': 'Instagram Capstone Copper Chile', 'valor_uf': 37.5, 'es_spot': False}
                ]
            },
            {
                'nombre': 'Capstone Mining Corp',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Proyecto HSE (julio-octubre 2025)', 'valor_uf': 200, 'es_spot': False},
                    {'nombre': 'Promedio mensual continuo', 'valor_uf': 300, 'es_spot': False}
                ]
            },
            {
                'nombre': 'NOVA AUSTRAL',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Asesoría Comunicacional', 'valor_uf': 115, 'es_spot': False}
                ]
            },
            {
                'nombre': 'OXZO S.A.',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Comunicaciones externas', 'valor_uf': 100, 'es_spot': False},
                    {'nombre': 'Linkedin', 'valor_uf': 60, 'es_spot': False}
                ]
            },
            {
                'nombre': 'SONNEDIX',
                'tipo': 'permanente',
                'servicios': [
                    {'nombre': 'Monitoreo de noticias diario', 'valor_uf': 40, 'es_spot': False}
                ]
            }
        ]

        # CLIENTES SPOT
        clientes_spot = [
            {
                'nombre': 'BCI',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Talleres de vocería promedio mensual', 'valor_uf': 53.1, 'es_spot': True}
                ]
            },
            {
                'nombre': 'Capital Advisors',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Sept-oct-nov promedio mensual', 'valor_uf': 20.8, 'es_spot': True}
                ]
            },
            {
                'nombre': 'Capstone - Diseño',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Diseño por 1 vez promedio mensual', 'valor_uf': 5.8, 'es_spot': True}
                ]
            },
            {
                'nombre': 'Capstone - Embajadores',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Embajadores por 1 vez promedio mensual', 'valor_uf': 5.4, 'es_spot': True}
                ]
            },
            {
                'nombre': 'Capstone - Vocería',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Un taller de vocería promedio mensual', 'valor_uf': 16.7, 'es_spot': True}
                ]
            },
            {
                'nombre': 'Concha y Toro',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Un Taller de vocería promedio mensual', 'valor_uf': 5, 'es_spot': True}
                ]
            },
            {
                'nombre': 'Embajada de Italia',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Asesoría comunicacional x 4 meses promedio mensual', 'valor_uf': 22.2, 'es_spot': True}
                ]
            },
            {
                'nombre': 'FALABELLA - Vocería',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Taller de vocería Una vez promedio mensual', 'valor_uf': 16.7, 'es_spot': True}
                ]
            },
            {
                'nombre': 'FRUTAS DE CHILE - Vocería',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Taller de vocería una vez promedio mensual', 'valor_uf': 16.7, 'es_spot': True}
                ]
            },
            {
                'nombre': 'OXZO - Diagnóstico',
                'tipo': 'spot',
                'servicios': [
                    {'nombre': 'Diagnóstico una vez promedio mensual', 'valor_uf': 17.5, 'es_spot': True}
                ]
            }
        ]

        # Cliente INTERNO: COMSULTING (para horas no facturables)
        cliente_interno = {
            'nombre': 'COMSULTING',
            'tipo': 'permanente',
            'servicios': [
                {'nombre': 'Horas Internas y Administrativas', 'valor_uf': 0, 'es_spot': False}
            ]
        }

        # Combinar todos los clientes (incluir COMSULTING al inicio)
        todos_clientes = [cliente_interno] + clientes_permanentes + clientes_spot

        total_clientes = 0
        total_servicios = 0
        total_ingresos_mes = 0

        for cliente_data in todos_clientes:
            # Crear cliente
            cliente = Cliente(
                nombre=cliente_data['nombre'],
                tipo=cliente_data['tipo'],
                activo=True
            )
            db.session.add(cliente)
            db.session.flush()  # Para obtener el ID
            total_clientes += 1

            print(f"\n{'='*70}")
            print(f"Cliente: {cliente_data['nombre']} ({cliente_data['tipo'].upper()})")
            print(f"{'='*70}")

            # Crear servicios del cliente
            for servicio_data in cliente_data['servicios']:
                servicio = ServicioCliente(
                    cliente_id=cliente.id,
                    nombre=servicio_data['nombre'],
                    valor_mensual_uf=servicio_data['valor_uf'],
                    es_spot=servicio_data['es_spot'],
                    activo=True
                )
                db.session.add(servicio)
                db.session.flush()  # Para obtener el ID
                total_servicios += 1
                total_ingresos_mes += servicio_data['valor_uf']

                print(f"  ✓ Servicio: {servicio_data['nombre'][:50]:50} | {servicio_data['valor_uf']:>8.2f} UF/mes")

                # Crear ingresos mensuales para todo el año
                for mes in range(1, 13):
                    ingreso = IngresoMensual(
                        servicio_id=servicio.id,
                        año=año_actual,
                        mes=mes,
                        ingreso_uf=servicio_data['valor_uf']
                    )
                    db.session.add(ingreso)

        db.session.commit()

        print("\n" + "="*80)
        print("IMPORTACIÓN COMPLETADA")
        print("="*80)
        print(f"Total clientes creados: {total_clientes}")
        print(f"Total servicios creados: {total_servicios}")
        print(f"Total ingresos mensuales: {total_ingresos_mes:.2f} UF/mes")
        print(f"Total ingresos anuales estimados: {total_ingresos_mes * 12:.2f} UF/año")
        print("="*80)

if __name__ == '__main__':
    importar_clientes_e_ingresos()
