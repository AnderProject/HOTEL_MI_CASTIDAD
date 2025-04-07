from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

class IVA(models.Model):
    porcentaje = models.DecimalField(max_digits=4, decimal_places=2)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.activo:
            IVA.objects.exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.porcentaje * 100}% IVA ({self.descripcion})"

    @classmethod
    def obtener_iva_activo(cls):
        return cls.objects.filter(activo=True).first() or cls.objects.create(porcentaje=Decimal('0.12'), descripcion='Por defecto')



class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cedula}"


class Reserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="reservas")
    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    numero_habitacion = models.IntegerField()
    duracion_reserva = models.IntegerField(default=3)
    horas_extras = models.IntegerField(default=0)
    historial = models.BooleanField(default=False) 

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Ocupada', 'Ocupada'),
        ('Limpieza', 'Limpieza'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendiente')
    precio_base = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('8.93'))
    precio_total = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('10.00'))
    iva_aplicado = models.ForeignKey(IVA, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas')


    def calcular_precio_total(self):
        iva_activo = IVA.obtener_iva_activo()
        self.iva_aplicado = iva_activo
        costo_horas_extras = Decimal(self.horas_extras) * Decimal('3.50')
        precio_sin_iva = self.precio_base + costo_horas_extras
        self.precio_total = round(precio_sin_iva * (Decimal('1') + iva_activo.porcentaje), 2)

    def save(self, *args, **kwargs):

        self.calcular_precio_total()
        super().save(*args, **kwargs)

    def tiempo_termino(self):
        inicio_reserva = datetime.combine(self.fecha_reserva, self.hora_reserva)
        return inicio_reserva + timedelta(hours=self.duracion_reserva + self.horas_extras)

    def horas_extra(self):
        ahora = timezone.now()
        fin_reserva = self.tiempo_termino()

        if timezone.is_naive(fin_reserva):
            fin_reserva = timezone.make_aware(fin_reserva)

        if ahora > fin_reserva:
            horas_extra = (ahora - fin_reserva).total_seconds() // 3600
            return int(horas_extra)
        return 0

    def ajustar_a_limpieza(self):

        self.estado = 'Limpieza'
        self.duracion_reserva = 0.17
        self.horas_extras = 0
        self.calcular_precio_total()
        self.save()

    def __str__(self):
        return f"{self.nombre_cliente} {self.apellido_cliente} - {self.fecha_reserva}"


class Factura(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='factura')
    fecha_emision = models.DateTimeField(default=datetime.now, editable=False)
    numero_factura = models.CharField(max_length=20, unique=True)
    total_a_pagar = models.DecimalField(max_digits=8, decimal_places=2)

    def calcular_total(self):
        self.reserva.calcular_precio_total()
        self.total_a_pagar = self.reserva.precio_total
        self.save()

    def save(self, *args, **kwargs):
        self.calcular_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.reserva.nombre_cliente}"


class Habitacion(models.Model):
    numero_habitacion = models.IntegerField()
    estado = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Habitación {self.numero_habitacion} - {self.estado}"