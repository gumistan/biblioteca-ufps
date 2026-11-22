"""
Carga datos de prueba para la fase 5 (Biblioteca UFPS).

Uso (con el entorno virtual activo, desde la carpeta donde esta manage.py):
    python cargar_datos.py

Es seguro ejecutarlo mas de una vez: usa get_or_create y no duplica nada.
No modifica ni borra los datos que ya existan.
"""
import os
from datetime import timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone  # noqa: E402

from biblioteca.models import (  # noqa: E402
    Autor, Categoria, Copia, Estudiante, Libro, Prestamo,
)

hoy = timezone.localdate()

# --- Categorias ---------------------------------------------------------
novela, _ = Categoria.objects.get_or_create(nombre="Novela")
ingenieria, _ = Categoria.objects.get_or_create(nombre="Ingeniería")
historia, _ = Categoria.objects.get_or_create(nombre="Historia")

# --- Autores (3) --------------------------------------------------------
garcia, _ = Autor.objects.get_or_create(nombre="Gabriel García Márquez")
sommerville, _ = Autor.objects.get_or_create(nombre="Ian Sommerville")
galeano, _ = Autor.objects.get_or_create(nombre="Eduardo Galeano")

# --- Libros (5) ---------------------------------------------------------
# (isbn, titulo, idioma, anio, categoria, [autores])
datos_libros = [
    ("978-0-00-000001-1", "Cien años de soledad", "Español", 1967, novela, [garcia]),
    ("978-0-00-000002-2", "Ingeniería de Software", "Español", 2011, ingenieria, [sommerville]),
    ("978-0-00-000003-3", "Las venas abiertas de América Latina", "Español", 1971, historia, [galeano]),
    ("978-0-00-000004-4", "Antología de ensayos latinoamericanos", "Español", 1990, historia, [garcia, galeano]),
    ("978-0-00-000005-5", "Crónica de una muerte anunciada", "Español", 1981, novela, [garcia]),
]

libros = []
for isbn, titulo, idioma, anio, categoria, autores in datos_libros:
    libro, _ = Libro.objects.get_or_create(
        isbn=isbn,
        defaults={
            "titulo": titulo,
            "idioma": idioma,
            "anio_publicacion": anio,
            "categoria": categoria,
        },
    )
    libro.autores.add(*autores)
    libros.append(libro)

l1, l2, l3, l4, l5 = libros

# --- Copias (8) ---------------------------------------------------------
# (codigo, libro, condicion)
datos_copias = [
    ("UFPS-001", l1, "usado"),
    ("UFPS-002", l1, "nuevo"),
    ("UFPS-003", l2, "nuevo"),
    ("UFPS-004", l2, "danado"),
    ("UFPS-005", l3, "usado"),
    ("UFPS-006", l4, "nuevo"),
    ("UFPS-007", l4, "usado"),
    ("UFPS-008", l5, "nuevo"),
]

copias = {}
for codigo, libro, condicion in datos_copias:
    copia, _ = Copia.objects.get_or_create(
        codigo=codigo, defaults={"libro": libro, "condicion": condicion}
    )
    copias[codigo] = copia

# --- Estudiantes (4) ----------------------------------------------------
datos_estudiantes = [
    ("1152001", "Ana Rojas", "ana.rojas@ufps.edu.co"),
    ("1152002", "Luis Pérez", "luis.perez@ufps.edu.co"),
    ("1152003", "Marta Gómez", "marta.gomez@ufps.edu.co"),
    ("1152004", "Carlos Díaz", "carlos.diaz@ufps.edu.co"),  # nunca pide prestado
]

est = {}
for codigo, nombre, correo in datos_estudiantes:
    e, _ = Estudiante.objects.get_or_create(
        codigo=codigo, defaults={"nombre": nombre, "correo": correo}
    )
    est[codigo] = e

ana, luis, marta, carlos = (est[c] for c in ("1152001", "1152002", "1152003", "1152004"))

# --- Prestamos (6) ------------------------------------------------------
# Solo se crean si estos estudiantes aun no tienen prestamos (evita duplicar).
if Prestamo.objects.filter(estudiante__in=[ana, luis, marta, carlos]).exists():
    print("Los préstamos de prueba ya existen. No se crean de nuevo.")
else:
    # (copia, estudiante, dias_desde_prestamo, dias_limite, dias_devolucion)
    # dias_* se cuentan hacia atras desde hoy; limite positivo = en el futuro.
    # dias_devolucion=None -> prestamo activo (sin devolver).
    datos_prestamos = [
        (copias["UFPS-001"], ana, 30, -16, 20),    # devuelto
        (copias["UFPS-001"], luis, 5, 9, None),    # ACTIVO (misma copia, despues de devolverse)
        (copias["UFPS-002"], ana, 25, -11, 15),    # devuelto
        (copias["UFPS-003"], marta, 20, -6, None), # ACTIVO y vencido
        (copias["UFPS-005"], luis, 15, -1, 10),    # devuelto
        (copias["UFPS-006"], marta, 3, 11, None),  # ACTIVO
    ]

    for copia, estudiante, dias_atras, dias_limite, dias_devol in datos_prestamos:
        p = Prestamo.objects.create(
            copia=copia,
            estudiante=estudiante,
            fecha_limite=hoy + timedelta(days=dias_limite),
        )
        # fecha_prestamo es auto_now_add: se ajusta con update() despues de crear.
        Prestamo.objects.filter(pk=p.pk).update(
            fecha_prestamo=hoy - timedelta(days=dias_atras),
            fecha_devolucion=None if dias_devol is None else hoy - timedelta(days=dias_devol),
        )

    print("Préstamos de prueba creados.")

print("Listo.")
print(
    f"Totales -> Autores: {Autor.objects.count()}, Libros: {Libro.objects.count()}, "
    f"Copias: {Copia.objects.count()}, Estudiantes: {Estudiante.objects.count()}, "
    f"Préstamos: {Prestamo.objects.count()}"
)
