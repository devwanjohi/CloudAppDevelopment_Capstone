from django.shortcuts import render
from django.http.response import Http404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')
# ...


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')
# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/e2c27cb3-f03d-49b6-a540-db62d7091f1c/dealership-package/get-dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        get_states = []
        for dealer in dealerships:
            get_states.append(dealer.st)
        just_states = set(get_states)

        context['dealers'] = dealerships
        context['states'] = sorted(just_states)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/e2c27cb3-f03d-49b6-a540-db62d7091f1c/dealership-package/get-review.json"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        # Concat all dealer's short name
        dealer_reviews = ' '.join([review.review for review in reviews])
        # Return a list of dealer short name
        return HttpResponse(dealer_reviews)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/e2c27cb3-f03d-49b6-a540-db62d7091f1c/dealership-package/post-review-sequence"
    context = {}
    # Check if user is  authenticated
    if request.user.is_authenticated:
        try:
            car = get_object_or_404(CarModel, pk=request.POST.get('car'))

            review = {
                'id': random.randint(100,200),
                'name': request.user.name,
                'dealership': dealer_id,
                'review': request.POST.get('review'),
                'purchase': request.POST.get('purchase', False),
                'purchase_date': request.POST.get('purchase_date', None),
                'car_make': car.car_make.name,
                'car_model': car.name,
                'car_year': car.car_year.year
            }
        except Http404:
            review = {
                'id': random.randint(100,200),
                'name': request.user.name,
                'dealership': dealer_id,
                'review': request.POST.get('review'),
                'purchase': request.POST.get('purchase', False)
            }
        json_payload = {"review": review}

        r = post_request(url, json_payload=json_payload, dealer_id=dealer_id)
        if r == 200:
            # context['status'] = 'Posted successfully!'
            print('Posteed successfully!')
        else:
            context['status'] = '[{}] Something went wrong on the server.'.format(r)
        review_view = redirect('djangoapp:dealer_details', dealer_id=dealer_id)
    return review_view