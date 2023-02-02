from django.contrib.auth import logout
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import View
# from django.views.generic import RedirectView
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL

    path(route='about/', view=views.AboutPageView.as_view(), name="about"),
    path(route='contact/', view=views.ContactPageView.as_view(), name="contact"),

    path(route='reg/', view=views.registration_request, name="reg"),

    path(route='login/', view=views.login_request, name="login"),
    path(route='logout/', view=views.logout_request, name="logout"),

    path(route='', view=views.get_dealerships, name='index'),
    # e.g. ..djangoapp/state/CA
    path(route='state/<str:state>/', view=views.get_state_dealers, name="state_dealers"), # mostly for testing

    # e.g. ..djangoapp/dealer/15/Tempsoft
    path(route='dealer/<int:dealer_id>/<str:dealer_sn>', view=views.get_dealer_details, name='dealer_details'),

    # e.g. ..djangoapp/review/15/Tempsoft
    path(route='review/<int:dealer_id>/<str:dealer_sn>', view=views.add_review, name='add_review'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)