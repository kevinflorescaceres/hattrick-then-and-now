from django.shortcuts import redirect, render
from django.conf import settings
from requests_oauthlib import OAuth1Session

def hattrick_login(request):
    oauth = OAuth1Session(
        settings.HATTRICK_CONSUMER_KEY,
        client_secret=settings.HATTRICK_CONSUMER_SECRET,
        callback_uri=request.build_absolute_uri('/hattrick/callback/')
    )
    
    try:
        fetch_response = oauth.fetch_request_token(settings.HATTRICK_REQUEST_TOKEN_URL)
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})
    
    request.session['resource_owner_key'] = fetch_response.get('oauth_token')
    request.session['resource_owner_secret'] = fetch_response.get('oauth_token_secret')
    
    authorization_url = oauth.authorization_url(settings.HATTRICK_AUTHORIZE_URL)
    return redirect(authorization_url)


def hattrick_callback(request):
    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')
    
    resource_owner_key = request.session.get('resource_owner_key')
    resource_owner_secret = request.session.get('resource_owner_secret')
    
    if not resource_owner_key or not resource_owner_secret:
        return render(request, 'error.html', {'error': 'Missing request token info in session.'})
    
    if oauth_token != resource_owner_key:
        return render(request, 'error.html', {'error': 'Returned token does not match stored token.'})
    
    oauth = OAuth1Session(
        settings.HATTRICK_CONSUMER_KEY,
        client_secret=settings.HATTRICK_CONSUMER_SECRET,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=oauth_verifier,
    )
    
    try:
        access_token_response = oauth.fetch_access_token(settings.HATTRICK_ACCESS_TOKEN_URL)
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})
    
    access_token = access_token_response.get('oauth_token')
    access_token_secret = access_token_response.get('oauth_token_secret')
    
    request.session['access_token'] = access_token
    request.session['access_token_secret'] = access_token_secret
    
    del request.session['resource_owner_key']
    del request.session['resource_owner_secret']
    
    return render(request, 'success.html', {
        'message': 'Authenticated with Hattrick!',
        'access_token': access_token,
        'access_token_secret': access_token_secret,
    })


def hattrick_test_endpoint(request):
    # Example: call a protected resource using stored access tokens
    
    access_token = request.session.get('access_token')
    access_token_secret = request.session.get('access_token_secret')
    
    if not access_token or not access_token_secret:
        return redirect('hattrick_login')  # or show error
    
    oauth = OAuth1Session(
        settings.HATTRICK_CONSUMER_KEY,
        client_secret=settings.HATTRICK_CONSUMER_SECRET,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    
    # Example endpoint for national players, passing team id 3026
    url = 'https://chpp.hattrick.org/chppxml.ashx?file=nationalplayers&teamID=3026'
    
    response = oauth.get(url)
    
    if response.status_code == 200:
        xml_data = response.text
        # You can parse XML or just display for now
        return render(request, 'xml_display.html', {'xml_data': xml_data})
    else:
        return render(request, 'error.html', {'error': f'API error: {response.status_code}'})

def get_players(request):
    oauth = OAuth1(
        config('HATTRICK_CONSUMER_KEY'),
        client_secret=config('HATTRICK_CONSUMER_SECRET'),
        resource_owner_key=request.session.get('oauth_token'),
        resource_owner_secret=request.session.get('oauth_token_secret'),
        signature_method='HMAC-SHA1'
    )

    url = 'https://chpp.hattrick.org/chppxml.ashx'
    params = {
        'file': 'players',
        'version': '3.3'
    }

    response = requests.get(url, auth=oauth, params=params)
    
    if response.status_code == 200:
        return HttpResponse(response.content, content_type='application/xml')
    else:
        return HttpResponse(f"Error {response.status_code}: {response.text}", status=response.status_code)