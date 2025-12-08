from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- VISTAS PRINCIPALES ---
    path('', views.Index, name='index'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('productos/', views.catalogo_completo, name='catalogo'),
    
    # --- USUARIOS ---
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('registro/', views.crear_cuenta, name='crear_cuenta'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('perfil/', views.perfil, name='perfil'),
    
    # --- PROCESO DE COMPRA ---
    path('procesar_orden/', views.procesar_orden, name='procesar_orden'),
    path('historial/', views.historial, name='historial'),
    path('buscar/', views.buscar, name='buscar'),

   
    # RECUPERACIÓN DE CONTRASEÑA (GMAIL)
    

    # Formulario donde el usuario pone su correo
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(template_name="password_reset.html"), 
         name='password_reset'),

    # Mensaje de éxito: "Correo enviado, revisa tu bandeja"
    path('reset_password_sent/', 
         auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), 
         name='password_reset_done'),

    # Link que llega al correo -> Formulario para poner la nueva clave
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), 
         name='password_reset_confirm'),

    # Mensaje final: "¡Listo! Contraseña cambiada"
    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), 
         name='password_reset_complete'),
]