from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.Index, name='index'),
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('registro/', views.crear_cuenta, name='crear_cuenta'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),

    # Formulario para pedir el correo
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(template_name="password_reset.html"), 
         name='password_reset'),

    # Mensaje de "Correo enviado"
    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), 
        name='password_reset_done'),

    #  Link que llega al correo (para poner la nueva clave)
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), 
        name='password_reset_confirm'),

    # Mensaje de "Contraseña cambiada con éxito"
    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), 
        name='password_reset_complete'),
        
    path('procesar_orden/', views.procesar_orden, name='procesar_orden'),

    path('historial/', views.historial, name='historial'),

    path('buscar/', views.buscar, name='buscar'),

    path('perfil/', views.perfil, name='perfil'),

    path('productos/', views.catalogo_completo, name='catalogo'),
]


