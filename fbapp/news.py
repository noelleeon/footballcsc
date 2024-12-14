from django.conf import settings
import requests

def newz(request):
    url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLNews"
    querystring = {"fantasyNews":"true","maxItems":"20"}
    headers = {
        "x-rapidapi-key": "57106580edmshaf54e7fc6006b35p145d26jsn76b265a565c0",
        "x-rapidapi-host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    resp = response.json()
    newz = resp['body']
    return {'newz':newz}
