# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import Reserva,Factura,Habitacion,Cliente
from .forms import ReservaForm, IVAForm, IVA
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.template.loader import get_template
from weasyprint import HTML
from decimal import Decimal
from django.urls import reverse
import tempfile
from django.utils.timezone import make_aware
from django.utils import timezone
from datetime import timedelta, datetime
from django.utils.timezone import now
import threading
import pandas as pd
import time


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            return redirect('dashboard')
        else:
            return redirect('login')

    else:
        return render(request, 'login.html') 

@login_required
def dashboard(request):
    total_reservas = Reserva.objects.count()
    reservas_por_fecha = Reserva.objects.values('fecha_reserva').annotate(total=Count('id'))
    habitaciones_populares = Reserva.objects.values('numero_habitacion').annotate(total=Count('id')).order_by('-total')[:10]
    habitaciones_disponibles = Habitacion.objects.filter(estado='Disponible').count()
    habitaciones_en_limpieza = Habitacion.objects.filter(estado='Limpieza').count()
    ultimas_reservas = Reserva.objects.order_by('-fecha_reserva')[:5]

    return render(request, 'principal/dashboard.html', {
        'total_reservas': total_reservas,
        'reservas_por_fecha': reservas_por_fecha,
        'habitaciones_populares': habitaciones_populares,
        'habitaciones_disponibles': habitaciones_disponibles,
        'habitaciones_en_limpieza': habitaciones_en_limpieza,
        'ultimas_reservas': ultimas_reservas,
    })


@login_required
def historial_listar_reservas(request):
    hoy = timezone.now().date()
    reservas_pendientes = Reserva.objects.filter(fecha_reserva=hoy, estado='Pendiente')
    reservas_ocupadas = Reserva.objects.filter(fecha_reserva=hoy, estado='Ocupada')
    reservas_finalizadas = Reserva.objects.filter(historial=True)

    return render(request, 'reservas/listar_reservas.html', {
        'reservas_pendientes': reservas_pendientes,
        'reservas_ocupadas': reservas_ocupadas,
        'reservas_finalizadas': reservas_finalizadas,
    })





@login_required
def listar_reservas(request):
    hoy = timezone.now().date()
    query = request.GET.get('q')
    reservas_list = Reserva.objects.select_related('cliente').all()
    if query:
        reservas_list = reservas_list.filter(
            Q(cliente__nombre__icontains=query) |
            Q(cliente__apellido__icontains=query) |
            Q(fecha_reserva__icontains=query) |
            Q(numero_habitacion__icontains=query)
        )

    reservas_pendientes = reservas_list.filter(fecha_reserva=hoy, estado='Pendiente')
    reservas_ocupadas = reservas_list.filter(fecha_reserva=hoy, estado='Ocupada')
    reservas_finalizadas = reservas_list.filter(historial=True)

    paginator_pendientes = Paginator(reservas_pendientes, 1000)
    paginator_ocupadas = Paginator(reservas_ocupadas, 1000)
    paginator_finalizadas = Paginator(reservas_finalizadas, 1000)

    pendientes_page = request.GET.get('pendientes_page')
    ocupadas_page = request.GET.get('ocupadas_page')
    finalizadas_page = request.GET.get('finalizadas_page')

    reservas_pendientes_page = paginator_pendientes.get_page(pendientes_page)
    reservas_ocupadas_page = paginator_ocupadas.get_page(ocupadas_page)
    reservas_finalizadas_page = paginator_finalizadas.get_page(finalizadas_page)

    return render(request, 'reservas/listar_reservas.html', {
        'reservas_pendientes': reservas_pendientes_page,
        'reservas_ocupadas': reservas_ocupadas_page,
        'reservas_finalizadas': reservas_finalizadas_page,
        'query': query,
    })


@login_required
def crear_reserva(request):
    duracion_rango = range(1, 4)
    horas_extra_rango = range(1, 6)

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        fecha_seleccionada = request.POST.get('fecha_reserva', timezone.now().date())
        habitaciones_ocupadas = Reserva.objects.filter(fecha_reserva=fecha_seleccionada, estado='Ocupada').values_list('numero_habitacion', flat=True)
        todas_las_habitaciones = range(2, 6)
        habitaciones_disponibles = [habitacion for habitacion in todas_las_habitaciones if habitacion not in habitaciones_ocupadas]

        if form.is_valid():
            nueva_reserva = form.save(commit=False)
            duracion_reserva = int(request.POST.get('duracion_reserva', 3))
            horas_extras = int(request.POST.get('horas_extras', 0))
            nueva_reserva.duracion_reserva = duracion_reserva
            nueva_reserva.horas_extras = horas_extras
            nueva_reserva.save()
            return redirect('listar_reservas')
    else:
        form = ReservaForm()
        fecha_seleccionada = request.GET.get('fecha_reserva', timezone.now().date())
        habitaciones_ocupadas = Reserva.objects.filter(fecha_reserva=fecha_seleccionada, estado='Ocupada').values_list('numero_habitacion', flat=True)
        todas_las_habitaciones = range(2, 6)
        habitaciones_disponibles = [habitacion for habitacion in todas_las_habitaciones if habitacion not in habitaciones_ocupadas]

    return render(request, 'reservas/crear_reserva.html', {
        'form': form,
        'habitaciones_disponibles': habitaciones_disponibles,
        'duracion_rango': duracion_rango,
        'horas_extra_rango': horas_extra_rango,
    })

def listar_iva(request):
    ivas = IVA.objects.all()
    return render(request, 'iva/listar_iva.html', {'ivas': ivas})

@login_required
def agregar_iva(request):
    if request.method == 'POST':
        form = IVAForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'IVA se ha creado correctamente.')
            return redirect('listar_iva')
    else:
        form = IVAForm()
    return render(request, 'iva/agregar_iva.html', {'form': form})

def editar_iva(request, iva_id):
    iva = get_object_or_404(IVA, id=iva_id)
    if request.method == 'POST':
        form = IVAForm(request.POST, instance=iva)
        if form.is_valid():
            form.save()
            return redirect('listar_iva')
    else:
        form = IVAForm(instance=iva)

    return render(request, 'iva/editar_iva.html', {'form': form})

@login_required
def activar_iva(request, iva_id):
    iva = IVA.objects.get(id=iva_id)
    IVA.objects.filter(activo=True).update(activo=False)
    
    if not iva.activo:
        IVA.objects.update(activo=False)
        iva.activo = True
        iva.save()
        
        messages.success(request, 'El IVA se ha activado correctamente.')
    else:
        messages.info(request, 'Este IVA ya está activo.')
    
    return redirect('listar_iva')



@login_required
def desactivar_iva(request, iva_id):
    # Desactivar el IVA seleccionado
    iva = get_object_or_404(IVA, id=iva_id)
    iva.activo = False
    iva.save()

    messages.success(request, 'Advertencia al no tener un IVA activo el Sistema optara por operar con el iva por defecto al 12%')
    return redirect(reverse('listar_iva'))

def eliminar_iva(request, iva_id):
    iva = get_object_or_404(IVA, id=iva_id)
    iva.delete()
    messages.success(request, "El IVA ha sido eliminado exitosamente.")
    return redirect('listar_iva')

@login_required
def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method == 'POST':
        data = request.POST.copy()
        data['duracion_reserva'] = reserva.duracion_reserva
        data['numero_habitacion'] = reserva.numero_habitacion
        data['fecha_reserva'] = reserva.fecha_reserva
        data['hora_reserva'] = reserva.hora_reserva
        form = ReservaForm(data, instance=reserva)

        if form.is_valid():
            # Guardar los cambios y recalcular el precio total
            reserva = form.save(commit=False)
            reserva.calcular_precio_total()
            reserva.save()
            return redirect('listar_reservas')
        else:
            # Imprimir errores en caso de que existan
            print(form.errors)
    else:
        form = ReservaForm(instance=reserva)

    return render(request, 'reservas/editar_reserva.html', {'form': form, 'reserva': reserva})

@login_required
def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        reserva.delete()
        return redirect('listar_reservas')
        
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})

@login_required
def historial_reservas(request):
    reservas_canceladas = Reserva.objects.filter(estado='Cancelada')
    return render(request, 'reservas/historial_reservas.html', {'reservas': reservas_canceladas})
@login_required
def cancelar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.estado = 'Cancelada'
    reserva.save()
    return redirect('listar_reservas')

@login_required
def disponibilidad_habitaciones(request):
    hoy = timezone.now().date()
    ahora = timezone.now().time()

    # Obtener habitaciones ocupadas cuya reserva sigue activa
    habitaciones_ocupadas = Reserva.objects.filter(
        fecha_reserva=hoy, 
        estado='Ocupada'
    ).values_list('numero_habitacion', flat=True)

    # Filtrar habitaciones en limpieza que aún están en proceso de limpieza
    habitaciones_limpieza = Reserva.objects.filter(
        fecha_reserva=hoy, 
        estado='Limpieza'
    ).values_list('numero_habitacion', flat=True)

    # Definir las 9 habitaciones del hotel
    todas_las_habitaciones = range(2, 6)

    # Calcular las habitaciones disponibles
    habitaciones_disponibles = [
        habitacion for habitacion in todas_las_habitaciones 
        if habitacion not in habitaciones_ocupadas and habitacion not in habitaciones_limpieza
    ]

    print(f"Habitaciones ocupadas: {habitaciones_ocupadas}")
    print(f"Habitaciones en limpieza: {habitaciones_limpieza}")
    print(f"Habitaciones disponibles: {habitaciones_disponibles}")

    # Pasar los datos al template
    return render(request, 'disponibilidad/disponibilidad_habitaciones.html', {
        'habitaciones_disponibles': habitaciones_disponibles,
        'habitaciones_ocupadas': habitaciones_ocupadas,
        'habitaciones_limpieza': habitaciones_limpieza,
    })




def generar_factura(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    reserva.calcular_precio_total()
    reserva.save()
    factura, creada = Factura.objects.get_or_create(
        reserva=reserva,
        defaults={
            'numero_factura': f"F-{reserva.id}-{reserva.fecha_reserva.strftime('%Y%m%d')}",
            'total_a_pagar': reserva.precio_total,
        }
    )
    if not creada:
        factura.total_a_pagar = reserva.precio_total
        factura.save()
    return render(request, 'facturas/factura.html', {'factura': factura, 'reserva': reserva})



def generar_factura_pdf(request, reserva_id):
    reserva = Reserva.objects.get(id=reserva_id)
    precio_total_decimal = Decimal(reserva.precio_total)
    subtotal = precio_total_decimal
    impuesto = round(precio_total_decimal * Decimal(0.12), 2)
    total = round(precio_total_decimal * Decimal(1.12), 2)

    factura_data = {
        'reserva': reserva,
        'factura': {
            'numero_factura': 'F-0001',
            'fecha_emision': timezone.now().strftime('%Y-%m-%d'),
            'subtotal': subtotal,
            'impuesto': impuesto,
            'total': total,
            'observaciones': 'Gracias por elegir nuestro hotel.',
        },
        'extras': []
    }

    html_string = render_to_string('reservas/factura.html', factura_data)
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()
    

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=factura_{reserva.id}.pdf'
    return response

@login_required
def cambiar_a_limpieza(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.estado = 'Limpieza'
    reserva.historial = True
    #tiempo de duracion de la habitacion en limpieza
    reserva.tiempo_termino = timezone.now() + timedelta(seconds=60)
    reserva.save()
    # Añadir mensaje de éxito
    messages.success(request, 'Habitacion enviada a Limpieza')

    # Programar el cambio de estado a "Disponible"
    def cambiar_a_disponible():
        reserva.estado = 'Disponible'
        reserva.save(update_fields=['estado'])

    timer = threading.Timer(20.0, cambiar_a_disponible)
    timer.start()
    return redirect('listar_reservas')


@login_required
def reporte_reservas_cliente(request):
    query = request.GET.get('q', '')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    reservas_list = Reserva.objects.all()
    if fecha_inicio and fecha_fin:
        reservas_list = reservas_list.filter(
            fecha_reserva__range=[fecha_inicio, fecha_fin]
        )
    if query:
        reservas_list = reservas_list.filter(
            Q(cliente__nombre__icontains=query) | Q(cliente__apellido__icontains=query)
        )
    clientes_con_reservas = reservas_list.values('cliente__nombre', 'cliente__apellido').annotate(
        total_reservas=Count('id')
    )

    context = {
        'clientes_con_reservas': clientes_con_reservas,
        'query': query,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'reservas/reporte_reservas_cliente.html', context)



def filtrar_y_descargar_reservas(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    reservas = Reserva.objects.all()

    if start_date and end_date:
        reservas = reservas.filter(fecha_reserva__range=[start_date, end_date])

    if 'descargar' in request.GET:
        
        data = {
            'Nombre Cliente': [reserva.cliente.nombre for reserva in reservas],
            'Apellido Cliente': [reserva.cliente.apellido for reserva in reservas],
            'Fecha Reserva': [reserva.fecha_reserva for reserva in reservas],
            'Número Habitación': [reserva.numero_habitacion for reserva in reservas],
                        'Duración Reserva (horas)': [reserva.duracion_reserva for reserva in reservas],
            'Horas Extras': [reserva.horas_extras for reserva in reservas],
            'IVA Aplicado': [f"{reserva.iva_aplicado.porcentaje * 100}%" if reserva.iva_aplicado else "No IVA" for reserva in reservas],
            'Precio Total': [reserva.precio_total for reserva in reservas],
        }
        
        df = pd.DataFrame(data)
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reservas_filtradas.xlsx"'
        df.to_excel(response, index=False)
        
        return response

    return render(request, 'reservas/filtrar_descargar_reservas.html', {
        'reservas': reservas,
        'start_date': start_date,
        'end_date': end_date,
    })


def buscar_cliente_por_cedula(request):
    cedula = request.GET.get('cedula')
    if cedula:
        try:
            cliente = Cliente.objects.get(cedula=cedula)
            data = {
                'nombre': cliente.nombre,
                'apellido': cliente.apellido,
                'existe': True
            }
        except Cliente.DoesNotExist:
            data = {'existe': False}
    else:
        data = {'existe': False}
    
    return JsonResponse(data)
