from django import forms
from .models import Reserva, Cliente
from django.core.exceptions import ValidationError
from datetime import date, time
from .models import IVA

class ReservaForm(forms.ModelForm):
    nombre_cliente = forms.CharField(max_length=100, required=True, label="Nombre Cliente")
    apellido_cliente = forms.CharField(max_length=100, required=True, label="Apellido Cliente")
    cedula_cliente = forms.CharField(max_length=10, required=True, label="Número de Cédula")

    class Meta:
        model = Reserva
        fields = ['fecha_reserva', 'hora_reserva', 'estado', 'duracion_reserva', 'horas_extras', 'numero_habitacion']

    def clean_cedula_cliente(self):
        cedula = self.cleaned_data.get('cedula_cliente')
        if len(cedula) != 10:
            raise ValidationError("La cédula debe tener exactamente 10 dígitos.")
        return cedula

    def clean_fecha_reserva(self):
        fecha_reserva = self.cleaned_data.get('fecha_reserva')
        if fecha_reserva < date.today():
            raise ValidationError("La fecha de reserva no puede ser en el pasado.")
        return fecha_reserva

    def clean_numero_habitacion(self):
        numero_habitacion = self.cleaned_data.get('numero_habitacion')
        if numero_habitacion <= 0:
            raise ValidationError("El número de habitación debe ser positivo.")
        return numero_habitacion
    
    def save(self, commit=True):
        cedula = self.cleaned_data.get('cedula_cliente')
        nombre = self.cleaned_data.get('nombre_cliente')
        apellido = self.cleaned_data.get('apellido_cliente')
        cliente, created = Cliente.objects.get_or_create(cedula=cedula, defaults={'nombre': nombre, 'apellido': apellido})
        self.instance.cliente = cliente
        return super().save(commit=commit)



class IVAForm(forms.ModelForm):
    class Meta:
        model = IVA
        fields = ['porcentaje', 'descripcion', 'activo']