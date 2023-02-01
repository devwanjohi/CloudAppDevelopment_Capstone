from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.CharField(max_length=20, null=False, default='Car Make')
    description = models.TextField(max_length=500, default="Description of the make of the car.")

    def __str__(self) -> str:
        return self.name + " - " + self.description

# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, default=1)
    name = models.CharField(null=False, max_length=20)
    dealer = models.IntegerField(null=False, default=0)

    CONVERT = 'convertible'
    HATCH = 'hatchback'
    SEDAN = 'sedan'
    SPORTS = 'sports'
    SUV = 'suv'
    VANS = 'vans'
    WAGON = 'wagon'
    CAR_TYPE_CHOICES = [
        (CONVERT, 'Convertible'),
        (HATCH, 'Hatchback'),
        (SEDAN, 'Sedan'),
        (SPORTS, 'Sports Car'),
        (SUV, 'SUV'),
        (VANS, 'Van'),
        (WAGON, 'Wagon'),
    ]
    car_type = models.CharField( max_length = 15, choices = CAR_TYPE_CHOICES, default = SUV )
    car_year = models.DateField()

    def __str__(self) -> str:
        return self.name + ": " + self.car_type + " - " + str(self.car_year.year)

# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
