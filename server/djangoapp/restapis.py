import requests
import json
from django.contrib.auth import authenticate
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from djangobackend.settings import NLU_SVC_OBJ
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

def get_request(url, **kwargs):
    print("\nGET from {} with paramaters {}".format(url,kwargs))
    try:
        if "api_key" in kwargs:
            api_key = kwargs.pop('apikey')
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = request.get(url, headers={'Content-type': 'application/json'}, params=kwargs)
    except:
    status_code = response.status_code
    json_data = json.loads(response.text)
    return json_data

def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, headers={'Content-type': 'application/json'}, json=json_payload)
    except:
    status_code = response.status_code
    return status_code
    
def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result.get("result", 'Could not pull results.')
        for dealer in dealers:
            dealer_obj = CarDealer(dealer)
            results.append(dealer_obj)

    return results

def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    if "dealer_id" in kwargs:
        json_result = get_request(url, dealerId=kwargs['dealerId'])
    if "result" in json_result:
        reviews = json_result.get("result")
        for review in reviews:
            review_obj = DealerReview(review)
            nlu_result = analyze_review_sentiments(review_obj.review)
            sentiment = ""
            if "sentiment" in nlu_result:
                sentiment = nlu_result['sentiment']['document']['label']
            elif "error" in nlu_result:
                sentiment = 'unknown ' + nlu_result.get("error")
            review_obj.sentiment = sentiment
            print("Review ID{} sentiment rating: {}".format(review_obj.id, review_obj.sentiment))
            results.append(review_obj)
    else:
        print('No entries received for Dealer Id {}'.format(kwargs.get('dealerId')))
        results = 'Could not retrieve review data: ' + json.get('error')
    return results

# Watson NLU Service

nlu_creds = NLU_SVC_OBJ[0].get('credentials')
authenticator = IAMAuthenticator(nlu_creds.get('apikey'))
service_url = nlu_creds.get('url')

nlu_instance = NaturalLanguageUnderstandingV1(
    version="2021-03-25",
    authenticator=authenticator
)
nlu_instance.set_service_url(service_url)

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
        return {'error': 'Something else broke while making the request. (;u; )'}