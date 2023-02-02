from django.db import models
from django.utils.timezone import now



class CarMake(models.Model):
    name = models.CharField(max_length=20, null=False, default='Car Make')
    description = models.TextField(max_length=500, default="Description of the make of the car.")

    def __str__(self) -> str:
        return self.name + " - " + self.description

class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, default=1)
    name = models.CharField(null=False, max_length=25)
    dealer = models.IntegerField(null=False, default=0)

    CONVERT = 'convertible'
    COUPE = 'coupe'
    ELECTRIC = 'electric'
    HATCH = 'hatchback'
    LIMO = 'limo'
    MUSCLE = 'muscle'
    SEDAN = 'sedan'
    SPORTS = 'sports'
    SUPER = 'super'
    SUV = 'suv'
    VANS = 'vans'
    WAGON = 'wagon'
    CAR_TYPE_CHOICES = [
        (CONVERT, 'Convertible'),
        (COUPE, 'Coupe'),
        (ELECTRIC, 'Electric Car'),
        (HATCH, 'Hatchback'),
        (LIMO, 'Limousine'),
        (MUSCLE, 'Muscle Car'),
        (SEDAN, 'Sedan'),
        (SPORTS, 'Sports Car'),
        (SUPER, 'Super Car'),
        (SUV, 'SUV'),
        (VANS, 'Van'),
        (WAGON, 'Wagon')
    ]
    car_type = models.CharField( max_length = 15, choices = CAR_TYPE_CHOICES, default = SUV )
    car_year = models.DateField()

    def __str__(self) -> str:
        return self.name + ": " + self.car_type + " - " + str(self.car_year.year)

class CarDealer:

    def __init__(self, kwargs):
        self.address = kwargs.get("address",'No Addres')
        self.city = kwargs.get("city", "Unknown")
        self.full_name = kwargs.get("full_name", "Unknown")
        self.id = kwargs.get("id", 0)
        self.lat = kwargs.get('lat', None)
        self.long = kwargs.get('long', None)
        self.short_name = kwargs.get('short_name', 'Unknown')
        self.st = kwargs.get('st', "NA")
        self.zip = kwargs.get('zip', 00000)

    def __str__(self):
        return self.full_name

class DealerReview:
    def __init__(self, kwargs):
        self.dealership = kwargs.get('dealership',1)
        self.name = kwargs.get('name', 'Anonymous Reviewer')
        self.purchase = kwargs.get('purchase', False)
        self.review = kwargs.get('review', 'No review.')
        self.purchase_date = kwargs.get('purchase_date', None)
        self.car_make = kwargs.get('car_make', None)
        self.car_model = kwargs.get('car_model', None)
        self.car_year = kwargs.get('car_year', None)
        self.id = kwargs.get('id', 123)
        self.sentiment = kwargs.get('sentiment', 'neutral')

    def __str__(self):
        return self.review