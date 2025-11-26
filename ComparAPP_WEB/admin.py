from django.contrib import admin
from .models import Categoria, Producto, Orden, DetalleOrden
from . models import Task

admin.site.register(Categoria)
admin.site.register(Producto)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title']

# Esto permite ver los productos DENTRO de la orden
class DetalleOrdenInline(admin.TabularInline):
    model = DetalleOrden
    extra = 0  # No muestra filas vacías extra
    readonly_fields = ('producto', 'cantidad', 'precio_al_momento') # Para que no se editen por error
    can_delete = False # Para no borrar historial accidentalmente

# Esto configura la lista principal de órdenes
class OrdenAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista
    list_display = ('id', 'usuario', 'fecha_creacion', 'total', 'estado')
    
    # Filtros laterales (para buscar rápido)
    list_filter = ('fecha_creacion', 'usuario')
    
    # Barra de búsqueda
    search_fields = ('usuario__username', 'id')
    
    # Agregamos el detalle de productos dentro
    inlines = [DetalleOrdenInline]

# Registramos el modelo con su configuración
admin.site.register(Orden, OrdenAdmin)

# Register your models here.
