from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    #Principal
    path('dashboard/', views.dashboard, name='dashboard'),

    #Reserva
    path('reservas/', views.listar_reservas, name='listar_reservas'),
    path('reservas/nueva/', views.crear_reserva, name='crear_reserva'),
    path('reservas/editar/<int:pk>/', views.editar_reserva, name='editar_reserva'),
    path('reservas/eliminar/<int:pk>/', views.eliminar_reserva, name='eliminar_reserva'),

    #Disponibilidad
    path('disponibilidad/', views.disponibilidad_habitaciones, name='disponibilidad_habitaciones'),
    path('reservas/cambiar_a_limpieza/<int:pk>/', views.cambiar_a_limpieza, name='cambiar_a_limpieza'),

    #Factura
    path('reservas/generar_factura/<int:reserva_id>/', views.generar_factura, name='generar_factura'),
    path('factura/<int:reserva_id>/pdf/', views.generar_factura_pdf, name='generar_factura_pdf'),
    path('buscar_cliente/', views.buscar_cliente_por_cedula, name='buscar_cliente_por_cedula'),
    
    #IVA
    path('iva/', views.listar_iva, name='listar_iva'),
    path('iva/agregar/', views.agregar_iva, name='agregar_iva'),
    path('iva/activar/<int:iva_id>/', views.activar_iva, name='activar_iva'),
    path('iva/desactivar/<int:iva_id>/', views.desactivar_iva, name='desactivar_iva'),
    path('iva/editar/<int:iva_id>/', views.editar_iva, name='editar_iva'),
    path('iva/eliminar/<int:iva_id>/', views.eliminar_iva, name='eliminar_iva'),

    #Reporte
    path('filtrar_descargar_reservas/', views.filtrar_y_descargar_reservas, name='filtrar_descargar_reservas'),

    #Inicio de Sesion
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', views.login_view, name='login'),
    
]
