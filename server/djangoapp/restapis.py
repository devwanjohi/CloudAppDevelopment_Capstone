# import requests
# import json
# # import related models here
# from requests.auth import HTTPBasicAuth
from os import name
from django.contrib.auth import authenticate
import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from djangobackend.settings import NLU_SVC_OBJ #IDEK if this is even right
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs, auth):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if api_key:
            # Basic authentication GET
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # no authentication GET
            response = request.get(url, params=params)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    response = requests.post(url, params=kwargs, json=json_payload)
    
# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result.get("result", 'Could not pull results.')
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_obj = CarDealer(dealer)
            # Create a CarDealer object with values in `doc` object
            # dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
            #                        id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
            #                        short_name=dealer_doc["short_name"],
            #                        st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    if "dealer_id" in kwargs:

        # Call get_request with a URL parameter
        json_result = get_request(url, dealerId=kwargs['dealerId'])
    if "result" in json_result:
        # Get the row list in JSON as dealers
        reviews = json_result.get("result")
        # For each dealer object
        for review in reviews:
            # Get its content in `doc` object
            review_obj = DealerReview(review)
            # Create a CarDealer object with values in `doc` object
            nlu_result = analyze_review_sentiments(review_obj.review)
            sentiment = ""
            if "sentiment" in nlu_result:
                sentiment = nlu_result['sentiment']['document']['label']
            elif "error" in nlu_result:
                sentiment = 'unknown ' + nlu_result.get("error")
            review_obj.sentiment = sentiment
            print("Review ID{} sentiment rating: {}".format(review_obj.id, review_obj.sentiment))
            # review_obj = DealerReview(dealership=review_doc["dealership"], name=review_doc["name"], purchase=review_doc["purchase"],
            #                        id=review_doc["id"], review=review_doc["review"], purchase_date=review_doc["purchase_date"],
            #                        car_make=review_doc["car_make"],
            #                        car_model=review_doc["car_model"], car_year=review_doc["car_year"])
            results.append(review_obj)
    else:
        print('No entries received for Dealer Id {}'.format(kwargs.get('dealerId')))
        results = 'Could not retrieve review data: ' + json.get('error')
    return results


# #
# Watson NLU Service
# #


nlu_creds = NLU_SVC_OBJ[0].get('credentials')
authenticator = IAMAuthenticator(nlu_creds.get('apikey'))
service_url = nlu_creds.get('url')

nlu_instance = NaturalLanguageUnderstandingV1(
    version="2021-03-25",
    authenticator=authenticator
)
nlu_instance.set_service_url(service_url)

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def analyze_review_sentiments(text):
    try:
        nlu_response = nlu_instance.analyze(
            text=text,
            features=features(
                sentiment=SentimentOptions(document=True)
            )
        ).get_result()

        return nlu_response
    except ApiException as ex:
        error_msg = "Error [{}]: {}".format(ex.code, ex.message)
        print(error_msg)
        return {'error': error_msg}
    except:
        # possibly failed to call get_request...
        return {'error': 'Something else broke while making the request. (;u; )'}
    # params = dict()
    # params["text"] = kwargs["text"]
    # params["version"] = kwargs["version"]
    # params["features"] = kwargs["features"]
    # params["return_analyzed_text"] = kwargs["return_analyzed_text"]
    # response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
    #                                 auth=HTTPBasicAuth('apikey', api_key))