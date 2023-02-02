from django.shortcuts import render
from django.http.response import Http404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random

logger = logging.getLogger(__name__)


def about(request):
    return render(request, 'djangoapp/about.html')

def contact(request):
    return render(request, 'djangoapp/contact.html')

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

def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

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

def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://1984d932.us-south.apigw.appdomain.cloud/api/dealerships"
        dealerships = get_dealers_from_cf(url)
        states = []
        for dealer in dealerships:
            states.append(dealer.st)
        just_states = set(states)

        context['dealers'] = dealerships
        context['states'] = sorted(just_states)
        return render(request, 'djangoapp/index.html', context)


def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://1984d932.us-south.apigw.appdomain.cloud/api/review"
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        context["dealer_id"] = dealer_id
        context["reviews"] = reviews
        return render(request, "djangoapp/dealer_details.html", context)

def add_review(request, dealer_id):
    url = "https://1984d932.us-south.apigw.appdomain.cloud/api/review"
    context = {}
    if request.method == "GET":
        cars = CarModel.objects.filter(dealership=dealer_id)
        context["dealer_id"] = dealer_id
        context["cars"] = cars
        review_view = render(request, "djangoapp/add_review", context)
    
    if request.method == "POST":    
        if request.user.is_authenticated:
            try:
                car = get_object_or_404(CarModel, pk=request.POST.get('car'))
                review = {
                    'id': random.randint(100,200),
                    'name': request.user.first_name + " " + request.user.last_name,
                    'dealership': dealer_id,
                    'review': request.POST.get('review'),
                    'purchase': request.POST.get('purchase', False),
                    'purchase_date': request.POST.get('purchase_date', None),
                    'car_make': request.POST.get('car_make'),
                    'car_model': request.POST.get('car_model'),
                    'car_year': request.POST.get('car_year')
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
                print('Posteed successfully!')
            else:
                context['status'] = '[{}] Something went wrong!'.format(r)
            review_view = redirect('djangoapp:dealer_details', dealer_id=dealer_id)
        return review_view