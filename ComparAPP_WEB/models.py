from django.db import models
from django.contrib.auth.models import User, AbstractUser


# PRODUCTOS Y CATEGORÍAS 


class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    
    # PRECIOS POR VENDEDOR 
    precio_castano = models.IntegerField(default=0, verbose_name="Precio Castaño")
    precio_foodtruck = models.IntegerField(default=0, verbose_name="Precio Foodtruck")
    precio_casino = models.IntegerField(default=0, verbose_name="Precio Casino")

    stock_castano = models.IntegerField(default=0, verbose_name="Stock Castaño")
    stock_foodtruck = models.IntegerField(default=0, verbose_name="Stock Foodtruck")
    stock_casino = models.IntegerField(default=0, verbose_name="Stock Casino")
    
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE) 
    nuevo = models.BooleanField(default=False) 

    def __str__(self):
        return self.nombre


# ORDENES 

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, default='Pendiente') 

    def __str__(self):
        return f"Orden {self.id} de {self.usuario.username}"

class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_al_momento = models.IntegerField() 

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"



class Task(models.Model):
    title = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.title

class Usuario(AbstractUser):
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_groups',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.'
    )