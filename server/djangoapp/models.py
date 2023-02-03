from os import name
from django.db import models
from django.db.models.fields.related import ManyToManyField
from django.utils.timezone import now

class CarMake(models.Model):
    mkid = models.SmallIntegerField(primary_key=True, default=1)
    name = models.CharField(max_length=25, null=False, default='Car Make')
    description = models.CharField(max_length=500, default="Description of car make or manufacturer.")

    def __str__(self) -> str:
        return self.name + " - " + self.description

class CarModel(models.Model):
    mdid = models.SmallIntegerField(primary_key=True, default=1)
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, default=1)
    name = models.CharField(null=False, max_length=25)
    dealership = models.IntegerField(null=False, default=0)
    SEDAN = 'sedan'
    SUV = 'suv'
    WAGON = 'wagon'
    COUPE = 'coupe'
    HATCH = 'hatchback'
    CONVERT = 'convertible'
    VANS = 'vans'
    SPORTS = 'sports'
    MUSCLE = 'muscle'
    SUPER = 'super'
    ELECTRIC = 'electric'
    LIMO = 'limo'
    CAR_TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Station Wagon'),
        (COUPE, 'Coupe'),
        (HATCH, 'Hatchback'),
        (CONVERT, 'Convertible'),
        (VANS, 'Van / Minivan'),
        (SPORTS, 'Sports Car'),
        (MUSCLE, 'Muscle Car'),
        (SUPER, 'Super Car'),
        (ELECTRIC, 'Electric Car'),
        (LIMO, 'Limousine')
    ]
    car_type = models.CharField(
        max_length = 15,
        choices = CAR_TYPE_CHOICES,
        default = COUPE
    )
    car_year = models.DateField()

    def __str__(self) -> str:
        return self.name + ": " + str(self.car_year.year) + " - " + self.car_type

class CarDealer:
    """
    Proxy that holds onto Dealer data returned from the get-all-dealers service
    Thus it's not a subclass of the Django Model... (just a container)
    Has a flexible constructor to account for possibly missing information.
        (And there seems to be one dealer in there like that...)
    """
    def __init__(self, kwargs):
        """
        kwargs should just be a dictionary
        """
        self.address = kwargs.get("address",'No Address Listed')
        self.city = kwargs.get("city", "Unknown City")
        self.full_name = kwargs.get("full_name", "Unnamed Dealership")
        self.id = kwargs.get("id", 0)
        self.lat = kwargs.get('lat', None)
        self.long = kwargs.get('long', None)
        self.short_name = kwargs.get('short_name', 'Unnamed')
        self.st = kwargs.get('st', "NA")
        self.zip = kwargs.get('zip', 00000)


    def __str__(self) -> str: 
        return "Dealer name: " + self.full_name

class DealerReview:
    """
    Proxy that holds onto Review data returned from the get-dealer-reivew service
    Thus it's not a subclass of the Django Model... (just a container)
    Has a flexible constructor to account for reviews missing information. 
        (e.g. an exsiting one for #13 with no purchase info)
    """
    def __init__(self, kwargs) -> None:
        """
        "kwargs" should just be a dictionary with all the data you need.
        """
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

    def __str__(self) -> str:
        return self.dealership + ": " + self.name + " - " + self.review