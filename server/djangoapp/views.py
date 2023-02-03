from django.http.response import Http404
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealer_by_state_from_cf, get_dealer_reviews_from_cf, get_dealers_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic.base import TemplateView
from datetime import datetime
import logging
import json
import random

logger = logging.getLogger(__name__)

class AboutPageView(TemplateView):
    template_name = 'djangoapp/about.html'

class ContactPageView(TemplateView):
    template_name = 'djangoapp/contact.html'

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['usr']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = 'Invalid username or password.'
            return render(request, 'djangoapp/login.html', context)
    else:
        context['message'] = 'Please login.'
        return render(request, 'djangoapp/login.html', context)

def logout_request(request):
    logger.debug("Logout user `{}`".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')


def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == "POST":
        username = request.POST['usr']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is a new user".format(username))

        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name,
                last_name=last_name, password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Sign up for a new account or login above."
            return render(request, 'djangoapp/registration.html', context)

REVIEW_API_URL = "https://1984d932.us-south.apigw.appdomain.cloud/api/review" 
DEALERSHIP_API_URL = "https://1984d932.us-south.apigw.appdomain.cloud/api/dealerships" 
STATE_DEALERS_API_URL = "https://1984d932.us-south.apigw.appdomain.cloud/api/state-dealers"


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = DEALERSHIP_API_URL
        dealerships = get_dealers_from_cf(url)
        get_states = []
        for dealer in dealerships:
            get_states.append(dealer.st)
        just_states = set(get_states)

        context['dealers'] = dealerships
        context['states'] = sorted(just_states)
        return render(request, 'djangoapp/index.html', context)


def get_state_dealers(request, state):
    context = {}
    if request.method == "GET":
        url = STATE_DEALERS_API_URL
        dealerships = get_dealer_by_state_from_cf(url, state=state)

        context['dealers'] = dealerships
        return render(request, 'djangoapp/state.html', context)


def get_dealer_details(request, dealer_id, dealer_sn):
    context = {}
    if request.method == "GET":
        url = REVIEW_API_URL
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)

        context['reviews'] = reviews
        context['dealer_id'] = dealer_id
        context['dealer_sn'] = dealer_sn
        return render(request, 'djangoapp/dealer_details.html', context)


def add_review(request, dealer_id, dealer_sn):
    url = REVIEW_API_URL
    context = {}

    if request.method == "GET":
        cars = CarModel.objects.filter(dealership=dealer_id)
        context['cars'] = cars
        context['dealer_id'] = dealer_id
        context['dealer_sn'] = dealer_sn
        review_view = render(request, 'djangoapp/add_review.html', context)

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
                    'car_make': car.car_make.name,
                    'car_model': car.name,
                    'car_year': car.car_year.year
                }
            except Http404:
                review = {
                    'id': random.randint(100,200),
                    'name': request.user.first_name + " " + request.user.last_name,
                    'dealership': dealer_id,
                    'review': request.POST.get('review'),
                    'purchase': request.POST.get('purchase', False)
                }

            json_payload = {"review": review}
            response_status = post_request(url, json_payload=json_payload, dealer_id=dealer_id)
            if response_status == 200:
                print('Posteed successfully!')
            else:
                context['status'] = '[{}] Something went wrong on the server.'.format(response_status)
        review_view = redirect('djangoapp:dealer_details', dealer_id=dealer_id, dealer_sn=dealer_sn)
    return review_view