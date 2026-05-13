# forms.py
from django import forms
from cars.models import Car, CarVideo

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand',
            'car_model',
            'category',
            'image',
            'prod_year',
            'price',
            'levy',
            'mileage',
            'fuel_type',
            'gear_box_type',
            'description',
            'color',
            'leather_interior',
            'drive_wheels',
            'doors',
            'wheel',
            'engine_volume',
            'cylinders',
            'airbags',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'engine_volume': forms.TextInput(attrs={
                'placeholder': 'Example: 2.0 or 2.0 Turbo'
            }),
            'mileage': forms.NumberInput(attrs={
                'placeholder': 'Mileage in KM'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': 'Price'
            }),
            'levy': forms.NumberInput(attrs={
                'placeholder': 'Leave empty if no levy'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['levy'].required = False
        self.fields['airbags'].required = False

class CarVideoForm(forms.ModelForm):
    class Meta:
        model = CarVideo
        fields = ['video']