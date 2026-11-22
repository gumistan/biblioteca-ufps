from django.db import models

# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.nombre

class Autor(models.Model):
    nombre = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = "Autores"
        
    def __str__(self):
        return self.nombre

class Libro(models.Model):
    titulo = models.CharField(max_length=150)
    idioma = models.CharField(max_length=120)
    anio_publicacion = models.IntegerField()
    isbn = models.CharField(max_length=20, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    autores = models.ManyToManyField(Autor)

    def __str__(self):
        return self.titulo

class Copia(models.Model):
    CONDICIONES = [
        ("nuevo", "Nuevo"),
        ("usado", "Usado"),
        ("danado", "Dañado"),
    ]
    condicion = models.CharField(max_length=10, choices=CONDICIONES, default="nuevo")
    codigo = models.CharField(max_length=20, unique=True)
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.libro.titulo} - {self.codigo}"

class Estudiante(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=120)
    correo = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Prestamo(models.Model):
    copia = models.ForeignKey(Copia, on_delete=models.PROTECT)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_limite = models.DateField()
    fecha_devolucion = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields=["copia"],
            condition=models.Q(fecha_devolucion__isnull=True),
            name="una_copia_un_prestamo_activo",
            violation_error_message="Esta copia ya está prestada y no ha sido devuelta.",
            )
        ]

# Alternativa documentada (no activa): validación con clean().
    # Requiere: from django.core.exceptions import ValidationError
    #
    # def clean(self):
    #     if self.copia_id and self.fecha_devolucion is None:
    #         otros = Prestamo.objects.filter(
    #             copia=self.copia, fecha_devolucion__isnull=True
    #         ).exclude(pk=self.pk)
    #         if otros.exists():
    #             raise ValidationError(
    #                 "Esta copia ya está prestada y no ha sido devuelta."
    #             )

    def __str__(self):
        return f"{self.copia} -> {self.estudiante}"