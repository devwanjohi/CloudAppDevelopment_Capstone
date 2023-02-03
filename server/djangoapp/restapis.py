from os import name
from django.contrib.auth import authenticate
import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from djangobackend.settings import NLU_SVC_OBJ
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
from ibm_watson.natural_language_understanding_v1 \
    import Features, SentimentOptions


def get_request(url, **kwargs):
    """
    Utility function to make HTTP GET requests
    """
    print("\nGET from {} with paramaters {}".format(url,kwargs))
    try:
        if 'apikey' in kwargs:
            api_key = kwargs.pop('apikey')
            print("Updated parameters: {}".format(kwargs))
            response = requests.get(url, headers={'Content-type': 'application/json'}, 
                params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-type': 'application/json'},
                params=kwargs)
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("Response Final URL {}".format(response.url))
    print("Response status {} \n".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def post_request(url, json_payload, **kwargs):
    """
    Utility function to make HTTP POST requests
    """
    print("POST to {} with paramaters {} \nIncludes payload: {}".format(url,kwargs, json_payload))
    try:
        response = requests.post(url, headers={'Content-type': 'application/json'}, 
            json=json_payload)
    except:
        print("Network exception occurred.")
    
    status_code = response.status_code
    print("Response Final URL {}".format(response.url))
    print("Response status {} \n".format(status_code))
    return status_code



def get_dealers_from_cf(url):
    """
    This function calls get_request() w/ the specified args then:
        1. Parses the json data returned from the request / "get-all-dealers" Cloud function
        2. Puts it into a proxy CarDealers obj.
        3. Creates and returns a list of those proxies.
    """
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result.get('entries','Could not pull entries.')
        for dealer in dealers:
            dealer_obj = CarDealer(dealer)
            results.append(dealer_obj)
    else:
        results = 'Could not pull dealers from database: ' + json_result.get('error', 'no error message provided.')

    return results


def get_dealer_by_state_from_cf(url, **kwargs):
    """
    This function calls get_request() w/ the specified args (state) then:
        1. Parses the json data returned from the request / "get-state-dealers" Cloud function
        2. Puts it into a proxy CarDealer obj
        3. Creates and returns a list of those proxies.
    """
    results = []
    if 'state' in kwargs:
        json_result = get_request(url, state=kwargs.get('state'))
    else:
        print('State (Abbrev.) not supplied in kwargs.')
        results.append('Could not execute request: missing state abbreviation')
    if 'entries' in json_result:
        dealers = json_result.get('entries','Could not pull entries.')

        for dealer in dealers:
            dealer_obj = CarDealer(dealer)
            print(dealer_obj.full_name)
            results.append(dealer_obj)
    else:
        print('No entries received for State {}'.format(kwargs.get('state','N/A')))
        results = 'Could not retrieve Dealer data for the given state.'
    return results


def get_dealer_reviews_from_cf(url, **kwargs):
    """
    This function calls get_request() w/ the specified args (dealerId) then:
        1. Parses the json data returned from the request / "get-dealer-reviews" Cloud function
        2. Puts it into a proxy DealerReviews obj.
        3. Creates and returns a list of those proxies.
    
    For some reason, this requires authentication be sent with the request... but is a public api.
    """
    results =[]
    if 'dealerId' in kwargs:
        json_result = get_request(url, dealerId=kwargs['dealerId'])
    else:
        print('Dealer ID not supplied in kwargs.')
        results.append("Could not execute request: missing Dealer ID")
    if 'entries' in json_result:
        reviews = json_result.get('entries')

        for review in reviews:
            review_obj = DealerReview(review)
            nlu_result = analyze_review_sentiments(review_obj.review)
            sentiment = ""
            if 'sentiment' in nlu_result:
                sentiment = nlu_result['sentiment']['document']['label']
            elif 'error' in nlu_result:
                sentiment = 'unknown ' + nlu_result.get('error')
            review_obj.sentiment = sentiment
            print("Review ID{} sentiment rating: {}".format(review_obj.id, review_obj.sentiment))
            results.append(review_obj)

    else:
        print('No entries received for Dealer Id {}'.format(kwargs.get('dealerId')))
        results = 'Could not retrieve review data: ' + json.get('error')
    return results


# #
# Watson NLU Service
# #


# nlu_creds = NLU_SVC_OBJ[0].get('credentials')
# authenticator = IAMAuthenticator(nlu_creds.get('apikey'))
# service_url = nlu_creds.get('url')

# nlu_instance = NaturalLanguageUnderstandingV1(
#     version="2021-03-25",
#     authenticator=authenticator
# )
# nlu_instance.set_service_url(service_url)

def analyze_review_sentiments(text):
    """
    1. Calls get_request() with specified args to Watson NLU service
    2. Returns the sentiment label
    """

    try:        
        nlu_response = nlu_instance.analyze(
            text=text,
            features=Features(
                sentiment=SentimentOptions(document=True)
            )
        ).get_result()     
        return nlu_response

    except ApiException as ex:
        error_msg = "Error [{}]: {}".format(ex.code, ex.message)
        print(error_msg)
        return {'error': error_msg}

    except:
        return {'error': 'Something else broke while making the request. (;u; )'}
        

