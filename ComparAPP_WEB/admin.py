from django.contrib import admin
from .models import Categoria, Producto, Orden, DetalleOrden, Task

# 1. Categorías (Registro simple)
admin.site.register(Categoria)

# 2. Productos (CONFIGURACIÓN NUEVA: Para ver los 3 precios)
class ProductoAdmin(admin.ModelAdmin):
    # Aquí definimos las columnas que se ven en la lista
    list_display = ('nombre', 'categoria', 'precio_castano', 'precio_foodtruck', 'precio_casino')
    # Filtro lateral por categoría
    list_filter = ('categoria',)
    # Barra de búsqueda
    search_fields = ('nombre',)

admin.site.register(Producto, ProductoAdmin)

# 3. Tasks (Lo que ya tenías)
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title']

# =================================================
# 4. CONFIGURACIÓN DE ÓRDENES (CARRITO)
# =================================================

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