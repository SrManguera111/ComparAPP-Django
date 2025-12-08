import json # Necesario para leer los datos que vienen de JavaScript
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import JsonResponse # Necesario para responder al JavaScript
from django.views.decorators.csrf import csrf_exempt # Para facilitar la recepción de datos
from django.contrib.auth.decorators import login_required # Para proteger la compra


from .models import Producto, Orden, DetalleOrden


# VISTAS DE NAVEGACIÓN Y PRODUCTOS


def Index(request):
    # Filtramos los productos por categoría
    empanadas = Producto.objects.filter(categoria__nombre='Empanadas')
    dulceria = Producto.objects.filter(categoria__nombre='Dulceria')
    bebestibles = Producto.objects.filter(categoria__nombre='Bebestibles')
    sandwiches = Producto.objects.filter(categoria__nombre='Sandwich')
    galletas = Producto.objects.filter(categoria__nombre='Galletas')

    context = {
        'empanadas': empanadas,
        'dulceria': dulceria,
        'bebestibles': bebestibles,
        'sandwiches': sandwiches,
        'galletas': galletas,
    }
    return render(request, 'index.html', context)

def nosotros(request):
    return render(request, 'nosotros.html')


# VISTAS DE USUARIOS (LOGIN / REGISTRO)


def iniciar_sesion(request):
    if request.method == 'POST':
        usuario = request.POST.get('nombre-usuario')
        contrasena = request.POST.get('contrasena')
        user = authenticate(request, username=usuario, password=contrasena)

        if user is not None:
            auth_login(request, user)
            return redirect('index') 
        else:
            return render(request, 'iniciar_sesion.html', {
                'error': 'Usuario o contraseña incorrectos'
            })
    return render(request, 'iniciar_sesion.html')

def cerrar_sesion(request):
    auth_logout(request)
    return redirect('index')

def crear_cuenta(request):
    if request.method == 'POST':
        username = request.POST.get('nombre-usuario')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        contrasena = request.POST.get('contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')

        if contrasena != confirmar_contrasena:
            return render(request, 'crear_cuenta.html', {'error': 'Las contraseñas no coinciden.'})
        if User.objects.filter(username=username).exists():
            return render(request, 'crear_cuenta.html', {'error': 'Este nombre de usuario ya está en uso.'})
        if User.objects.filter(email=email).exists():
            return render(request, 'crear_cuenta.html', {'error': 'Este correo electrónico ya está registrado.'})

        user = User.objects.create_user(username=username, email=email, password=contrasena)
        user.first_name = nombre
        user.last_name = apellido
        user.save()

        return redirect('iniciar_sesion')
    return render(request, 'crear_cuenta.html')


# PROCESAR ORDEN (CON STOCK)


@login_required(login_url='iniciar_sesion')
@csrf_exempt
def procesar_orden(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            carrito = data.get('carrito', [])
            total = data.get('total', 0)

            # Crear la Orden General
            orden = Orden.objects.create(
                usuario=request.user,
                total=total
            )

            # Recorrer el carrito para guardar detalles y RESTAR STOCK
            for item in carrito:
                producto_id = item.get('id')
                cantidad = int(item.get('quantity', 1))
                vendedor = item.get('vendor') 
                precio = item.get('price')

                # Obtener el producto real de la base de datos
                producto_db = Producto.objects.get(id=producto_id)

                # --- LÓGICA DE STOCK ---
                if vendedor == "Castaño":
                    if producto_db.stock_castano >= cantidad:
                        producto_db.stock_castano -= cantidad
                    else:
                        return JsonResponse({'status': 'error', 'message': f'Sin stock suficiente en Castaño para: {producto_db.nombre}'})
                
                elif vendedor == "Foodtruck":
                    if producto_db.stock_foodtruck >= cantidad:
                        producto_db.stock_foodtruck -= cantidad
                    else:
                        return JsonResponse({'status': 'error', 'message': f'Sin stock suficiente en Foodtruck para: {producto_db.nombre}'})

                elif vendedor == "Casino":
                    if producto_db.stock_casino >= cantidad:
                        producto_db.stock_casino -= cantidad
                    else:
                        return JsonResponse({'status': 'error', 'message': f'Sin stock suficiente en Casino para: {producto_db.nombre}'})
                
                # Guardar el nuevo stock en la BD
                producto_db.save()

                DetalleOrden.objects.create(
                    orden=orden,
                    producto=producto_db,
                    cantidad=cantidad,
                    precio_unitario=precio,  
                    subtotal=precio * cantidad
                )

            return JsonResponse({'status': 'success', 'orden_id': orden.id})

        except Producto.DoesNotExist:
             return JsonResponse({'status': 'error', 'message': 'Un producto no fue encontrado'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


# VISTAS DE HISTORIAL Y PERFIL

@login_required(login_url='iniciar_sesion')
def historial(request):
    # Buscamos las órdenes del usuario logueado
    mis_ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    return render(request, 'historial.html', {
        'ordenes': mis_ordenes
    })

def buscar(request):
    query = request.GET.get('q') # Obtenemos lo que escribió el usuario
    resultados = []

    if query:
        resultados = Producto.objects.filter(nombre__icontains=query)
    
    return render(request, 'resultados.html', {
        'resultados': resultados,
        'query': query
    })

@login_required(login_url='iniciar_sesion')
def perfil(request):
    user = request.user 

    if request.method == 'POST':
        user.first_name = request.POST.get('nombre')
        user.last_name = request.POST.get('apellido')
        user.email = request.POST.get('email')
        
        user.save()
        
        return render(request, 'perfil.html', {
            'mensaje': '¡Datos actualizados correctamente!'
        })

    return render(request, 'perfil.html')

def catalogo_completo(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {
        'productos': productos
    })