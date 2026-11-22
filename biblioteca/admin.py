from django.contrib import admin
from .models import Categoria, Autor, Libro, Copia, Estudiante, Prestamo
from django.utils import timezone
# Register your models here.


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display=("nombre",)

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display=("nombre",)
    search_fields=("nombre",)

class CopiaInline(admin.TabularInline):
    model = Copia
    extra = 1

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display=("isbn", "titulo", "idioma", "anio_publicacion", "categoria", "ver_autores")
    search_fields=("titulo", "isbn", "autores__nombre")
    list_filter=("categoria", "idioma")
    inlines = [CopiaInline]
    list_select_related=("categoria",)

    @admin.display(description="Autores")
    def ver_autores(self, obj):
        return ", ".join(a.nombre for a in obj.autores.all())

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("autores")

@admin.register(Copia)
class CopiaAdmin(admin.ModelAdmin):
    list_display=("codigo", "libro", "condicion")
    search_fields=("codigo", "libro__isbn", "libro__titulo")
    list_filter=("condicion",)
    list_select_related =("libro",)

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display=("codigo", "nombre", "correo")
    search_fields=("codigo", "nombre")
 
@admin.action(description="Marcar préstamos como devueltos")
def marcar_devueltos(modeladmin, request, queryset):
    queryset.update(fecha_devolucion__isnull=True).update(
        fecha_devolucion=timezone.localdate()
    )

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display=("copia", "estudiante", "fecha_prestamo", "fecha_limite", "fecha_devolucion", "devuelto")
    search_fields=("estudiante__nombre", "estudiante__codigo", "copia__codigo", "copia__libro__titulo", "copia__libro__isbn" )
    list_filter=("fecha_prestamo", "fecha_devolucion")
    readonly_fields=("fecha_prestamo", )
    actions=[marcar_devueltos]
    list_select_related =("copia__libro", "estudiante")

    @admin.display(boolean=True, description="¿Devuelto?")
    def devuelto(self, obj):
        return obj.fecha_devolucion is not None

