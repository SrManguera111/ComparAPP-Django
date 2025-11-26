import json # Necesario para leer los datos que vienen de JavaScript
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import JsonResponse # Necesario para responder al JavaScript
from django.views.decorators.csrf import csrf_exempt # Para facilitar la recepción de datos
from django.contrib.auth.decorators import login_required # Para proteger la compra


# Importamos tus modelos (Asegúrate de que Orden y DetalleOrden estén en models.py)
from .models import Producto, Orden, DetalleOrden

# ==========================================
# VISTAS DE NAVEGACIÓN Y PRODUCTOS
# ==========================================

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

# ==========================================
# VISTAS DE USUARIOS (LOGIN / REGISTRO)
# ==========================================

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

# ==========================================
# NUEVA VISTA: PROCESAR ORDEN (CARRITO)
# ==========================================

@csrf_exempt 
@login_required(login_url='iniciar_sesion') # Si el usuario no está logueado, lo manda al login
def procesar_orden(request):
    if request.method == 'POST':
        try:
            # 1. Obtener los datos enviados por JS (carrito y total)
            data = json.loads(request.body)
            carrito = data.get('carrito', [])
            total_cliente = data.get('total', 0)

            # 2. Crear la Orden principal vinculada al usuario actual
            nueva_orden = Orden.objects.create(
                usuario=request.user, 
                total=total_cliente
            )

            # 3. Crear los detalles (items) de esa orden
            for item in carrito:
                producto = Producto.objects.get(id=item['id'])
                DetalleOrden.objects.create(
                    orden=nueva_orden,
                    producto=producto,
                    cantidad=item['quantity'],
                    precio_al_momento=item['price']
                )
            
            # Respondemos "success" y el ID de la orden para usarlo en el QR
            return JsonResponse({'status': 'success', 'orden_id': nueva_orden.id})

        except Exception as e:
            # Si algo falla, enviamos el error para verlo en consola
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

#Para poder ver el historial de usuario
@login_required(login_url='iniciar_sesion')
def historial(request):
    # 1. Buscamos las órdenes del usuario logueado
    # order_by('-fecha_creacion') hace que salgan las más nuevas primero
    mis_ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    return render(request, 'historial.html', {
        'ordenes': mis_ordenes
    })

def buscar(request):
    query = request.GET.get('q') # Obtenemos lo que escribió el usuario en el input 'q'
    resultados = []

    if query:
        # Aquí ocurre la magia: __icontains busca coincidencias parciales
        # Buscamos por nombre del producto
        resultados = Producto.objects.filter(nombre__icontains=query)
    
    return render(request, 'resultados.html', {
        'resultados': resultados,
        'query': query
    })

@login_required(login_url='iniciar_sesion')
def perfil(request):
    user = request.user # Obtenemos al usuario actual

    if request.method == 'POST':
        # Recibimos los datos del formulario
        user.first_name = request.POST.get('nombre')
        user.last_name = request.POST.get('apellido')
        user.email = request.POST.get('email')
        
        # Guardamos en la base de datos
        user.save()
        
        # Mostramos mensaje de éxito
        return render(request, 'perfil.html', {
            'mensaje': '¡Datos actualizados correctamente!'
        })

    # Si no es POST, mostramos la página normal
    return render(request, 'perfil.html')

def catalogo_completo(request):
    # 1. Traemos todos los productos sin filtrar por categoría
    productos = Producto.objects.all()
    
    # 2. Enviamos la lista a la nueva plantilla
    return render(request, 'productos.html', {
        'productos': productos
    })