from django.contrib import admin
from .models import CarMake, CarModel

class CarModelInline:
    model = CarModel

class CarModelAdmin:
    list_display = ['name']

class CarMakeAdmin:
    inlines = [CarModelInline]
    list_display = ('name', 'car_year')
    list_filter = ['car_type']
    search_fields = ['name','car_year','car_type']

admin.site.register(CarMake)
admin.site.register(CarModel)