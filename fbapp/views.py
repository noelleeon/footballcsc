import os
import json
import random
import traceback
import requests
import nfl_data_py as nfl
import pytz
from datetime import datetime, timezone
import asyncio
from django.db import models
from django.contrib import messages
from fbapp.models import Member
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, StreamingHttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template import loader
from django.core.cache import cache
from django import template
from dotenv import load_dotenv
import openai
from openai import OpenAI
from channels.routing import ProtocolTypeRouter
from typing import AsyncGenerator
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# https://medium.com/@resshin24/how-to-connect-the-mysql-database-in-python-django-9433a243da8e
# ^^^ How to use the mysql db in my views.py file

#https://www.geeksforgeeks.org/using-python-environment-variables-with-python-dotenv/
load_dotenv()
#https://github.com/Kouidersif/openai-API/blob/main/openapp/views.py
#https://www.geeksforgeeks.org/openai-python-api/
client = OpenAI(api_key=os.environ.get("OPEN_API_KEY"))

#https://stackoverflow.com/questions/1070398/how-to-assign-a-value-to-a-variable-in-a-django-template
register = template.Library()

# https://www.geeksforgeeks.org/user-authentication-system-using-django/
###################################################
# Function: fbapp                                 #///////////////////////////////////
# Description: This is the landing page of my app #/////////////////////////////////
# Parameters: request (to request to html)        #//////////////////////////////////
# Return value: render -> rendered html file      #/////////////////////////////////
###################################################
def fbapp(request):
    return render(request, "myfirst.html")

###################################################
# Function: signupto                              #/////////////////////////////////
# Description: this gets called by a button to    #/////////////////////////////////
# redirect to the sign up page                    #//////////////////////////////////
# Parameters: request (to request the html)       #/////////////////////////////////
# Return value: redirect -> to another route      #/////////////////////////////////
###################################################
def signupto(request):
    return redirect('signup')

###################################################
# Function: signinto                              #/////////////////////////////////
# Description: this gets called by a button to    #/////////////////////////////////
# redirect to the sign in page                    #//////////////////////////////////
# Parameters: request (to request the html)       #/////////////////////////////////
# Return value: redirect -> to another route      #//////////////////////////////////
###################################################
def signinto(request):
    return redirect('signin')

###################################################
# Function: signup                                #////////////////////////////////////
# Description: this collects a form and signs the #///////////////////////////////////
# user up. If valid the page directs to dash if   #////////////////////////////////
# not valid the page directs to the home page.    #///////////////////////////////////
# Parameters: request (to request the html)       #//////////////////////////////////
# Return value: redirect -> to another route      #/////////////////////////////////////
###################################################
# https://forum.djangoproject.com/t/how-do-i-make-signup-page-available-only-for-logged-in-staff-users-in-django-allauth/12868/3
# https://www.geeksforgeeks.org/user-authentication-system-using-django/
@csrf_protect
def signup(request):
    if request.method == 'POST':
        print("the request is post")
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return render(request, "myfirst.html")
        #https://stackoverflow.com/questions/3090302/how-do-i-get-the-object-if-it-exists-or-none-if-it-does-not-exist-in-django
        if Member.objects.filter(username=username).exists():
            messages.error(request, "Snooze you lose! Choose a different username")
            return render(request, "signup.html")
        #https://stackoverflow.com/questions/41332528/how-to-hash-django-user-password-in-django-rest-framework
        #https://stackoverflow.com/questions/25098466/how-to-store-django-hashed-password-without-the-user-object
        try:
            hashpass = make_password(password)
            user = Member(username=username)
            user.set_password(password)
            user.save()
        #https://stackoverflow.com/questions/2293291/create-a-session-in-django
            messages.success(request, "You've been drafted! Play hard")
            login(request, user)
            return redirect('dash')
        except Exception as e:
            error_message = f"Error: {str(e)}\n{traceback.format_exc()}"
            messages.error(request, error_message)
            #messages.error(request, f"Error: {str(e)}")
            return render(request, "signup.html")
    return render(request, "signup.html")

###################################################
# Function: signin                                #//////////////////////////////
# Description: this collects a form and signs the #//////////////////////////////
# user in. If valid the page directs to dash if   #////////////////////////////
# not valid the page directs to the home page.    #//////////////////////////////
# Parameters: request (to request the html)       #/////////////////////////////
# Return value: redirect -> to another route      #/////////////////////////////
###################################################
@csrf_protect
def signin(request): 
    # if the http method is post grab the entered username and password
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        #https://docs.djangoproject.com/en/5.1/topics/auth/default/#:~:text=To%20log%20a%20user%20in,session%2C%20using%20Django's%20session%20framework.
        user = authenticate( request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, "Touchdown! Don't fumble this.")
            return redirect('dash')
        else:
            messages.info(request, "Either the user doesn't exist or you forgot your password.")
            return render(request, "signin.html")
    return render(request, "signin.html")

###################################################
# Function name: signout                          #/////////////////////////////////////////////////
# Description: Signs the user out and clears sess #////////////////////////////////////////////
# Parameters: request                             #///////////////////////////////////////////
# Return value: redirects to signin               #/////////////////////////////////////////////
###################################################
#https://stackoverflow.com/questions/76644005/request-session-clear-vs-request-session-flush-in-django
@login_required
def signout(request):
    if request.method == 'POST':
        logout(request)
        request.session.flush()
        return redirect('signin')

###################################################
# Function name: searchnav                        #
# Description: this is the ai bot named tank      #
# Parameters: Request                             #
# Return value: answer about a given question.    #
###################################################
#https://community.openai.com/t/questions-about-assistant-threads/485239
#Provided from code section of the openAI project
#https://platform.openai.com/docs/overview?lang=python
#https://stackoverflow.com/questions/77444332/openai-python-package-error-chatcompletion-object-is-not-subscriptable
@csrf_exempt
@login_required
def tankbar(request):
    answer = None
    print(request.method)
    if request.method == 'POST':
        try:
            if not request.body:
                return JsonResponse({'error_message': 'Empty request body'}, status=400)
            print(request.body)
            data = json.loads(request.body)
            question = data.get("question")
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                {"role":"system","content":"You are a helpful assistant who answers only questions about American football, anything ranging to players, news, teams, history, or statistics. You talk like an American football coach who talks a lot of smack. If someone asks you about anything other than American football you tell them to get lost."},
                {"role":"user","content":question}]
            )
            complete_dict = completion.model_dump()
            answer = complete_dict['choices'][0]['message']['content']
            return JsonResponse({'answer':answer})
        except Exception as e:
            error_message = f"Error: {str(e)}\n{traceback.format_exc()}"
            return JsonResponse({'error_message': error_message}, status=500)
    return JsonResponse({'message':'yo'}, status=200)

@login_required
def bheader(request):
    return render(request, "bheader.html")

@login_required
def dash(request):
    return render(request, "dashboard.html")

@login_required
def profile(request):
    return render(request, "profile.html")

@login_required
def teamprofile(request):
    tid = request.POST.get('team')
    if tid is not None:
        return redirect('teamchoice', tid=tid)
    else:
        return render(request, "teamprofile.html")

#https://reintech.io/blog/connecting-to-external-api-in-django
@login_required
def teamchoice(request, tid):
    url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLTeams"
    querystring = {"sortBy":"standings","rosters":"false","schedules":"false","topPerformers":"true","teamStats":"true"}
    headers = {"x-rapidapi-key": "57106580edmshaf54e7fc6006b35p145d26jsn76b265a565c0",
    "x-rapidapi-host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"}
#https://stackoverflow.com/questions/12353288/getting-values-from-json-using-python
#https://stackoverflow.com/questions/59074990/how-to-iterate-through-json-object-in-python-and-get-key
    response = requests.get(url, headers=headers, params=querystring)
    startr = response.json()
    for team in startr['body']:
        if team['teamID'] == tid: 
            # General team stuff for top of team card   
            nflComLogo1 = team['nflComLogo1']
            teamName = team['teamName']
            teamAbv = team['teamAbv']
            teamCity = team['teamCity']
            conferenceAbv = team['conferenceAbv']
            division = team['division']
     
            teamstats = team['teamStats']

            # [Rushing]
            rushing = teamstats['Rushing']
            #rushYds
            rushYds = rushing['rushYds']
            #carries
            carries = rushing['carries']
            #rushTD
            rushTD = rushing['rushTD']

            # [Kicking]
            kicking = teamstats['Kicking']
            #fgAttempts
            fgAttempts = kicking['fgAttempts']
            #fgMade
            fgMade = kicking['fgMade']
            #xpMade
            xpMade = kicking['xpMade']
            #fgYds
            fgYds = kicking['fgYds']
            #kickYards
            kickYards = kicking['kickYards']
            #xpAttempts
            xpAttempts = kicking['xpAttempts']

            # [Passing]
            passing = teamstats['Passing']
            #passAttempts
            passAttempts = passing['passAttempts']
            #passTD
            passTD = passing['passTD']
            #passYds
            passYds = passing['passYds']
            #int
            intercept = passing['int']
            #passCompletions
            passCompletions = passing['passCompletions']

            # [Punting]
            punting = teamstats['Punting']
            #puntYds
            puntYds = punting['puntYds']
            #punts
            punts = punting['punts']

            # [Receiving]
            receiving = teamstats['Receiving']
            #receptions
            receptions = receiving['receptions']
            #recTD
            recTD = receiving['recTD']
            #targets
            targets = receiving['targets']
            #recYds
            recYds = receiving['recYds']

            # [Defense]
            defense = teamstats['Defense']
            #fumblesLost
            fumblesLost = defense['fumblesLost']
            #defTD
            defTD = defense['defTD']
            #fumblesRecovered
            fumblesRecovered = defense['fumblesRecovered']
            #qbHits
            qbHits = defense['qbHits']
            #passDeflections
            passDeflections = defense['passDeflections']
            #totalTackles
            totalTackles = defense['totalTackles']
            #defensiveInterceptions
            defensiveInterceptions = defense['defensiveInterceptions']
            #rushingYardsAllowed
            rushingYardsAllowed = defense['rushingYardsAllowed']
            #sacks
            sacks = defense['sacks']
            #rushingTDAllowed
            rushingTDAllowed = defense['rushingTDAllowed']
     
            return render(request, 'teamchoice.html', {'nflComLogo1':nflComLogo1,'teamName':teamName,'teamAbv':teamAbv,'teamCity':teamCity,'conferenceAbv':conferenceAbv,'division':division,'rushYds':rushYds,'carries':carries,'rushTD':rushTD,'fgAttempts':fgAttempts,'fgMade':fgMade,'xpMade':xpMade,'fgYds':fgYds,'kickYards':kickYards,'xpAttempts':xpAttempts,'passAttempts':passAttempts,'passTD':passTD,'passYds':passYds,'intercept':intercept,'passCompletions':passCompletions,'puntYds':puntYds,'punts':punts,'receptions':receptions,'recTD':recTD,'targets':targets,'recYds':recYds,'fumblesLost':fumblesLost,'defTD':defTD,'fumblesRecovered':fumblesRecovered,'qbHits':qbHits,'passDeflections':passDeflections,'totalTackles':totalTackles,'defensiveInterceptions':defensiveInterceptions,'rushingYardsAllowed':rushingYardsAllowed,'sacks':sacks,'rushingTDAllowed':rushingTDAllowed})
    
@login_required
def playerprofile(request):
    #Url and header for grabbing single player from different api
    manyurl = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLPlayerList"
    manyheaders = {
        "x-rapidapi-key": "57106580edmshaf54e7fc6006b35p145d26jsn76b265a565c0",
        "x-rapidapi-host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
    }
    response = requests.get(manyurl, headers=manyheaders)
    manyresp = response.json()
    manyrespo = []    
    #https://medium.com/geekculture/web-scraping-tables-in-python-using-beautiful-soup-8bbc31c5803e
    #https://stackoverflow.com/questions/34144389/how-to-get-value-from-tables-td-in-beautifulsoup
    for player in manyresp['body']:
        playerz = {
            'espnHeadshot':player.get('espnHeadshot', 'N/A'),
            'espnName':player.get('espnName', 'N/A'),
            'team':player.get('team', 'N/A'),
            'jerseyNum':player.get('jerseyNum','N/A'),
            'playerID':player.get('playerID','N/A'),
            'teamID':player.get('teamID', 'N/A'),
        }
        manyrespo.append(playerz)

    #the data is so big the paginator makes it a bit quicker to load
    #https://www.geeksforgeeks.org/how-to-add-pagination-in-django-project/#
    pag = Paginator(manyrespo, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = pag.get_page(page_number)#returns the desred page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = pag.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = pag.page(pag.num_pages)
    return render(request, "playerprofile.html", {'manyrespo':manyrespo,'page_obj':page_obj})

@login_required
def playerchoice(request, playerID):
    return render(request, 'playerchoice.html', {'playerID':playerID})

@login_required
def stat(request):
    return render(request, "stat.html")

@login_required
def articles(request):
    return render(request, "articles.html")

@login_required
def article(request):
    return render(request, "article.html")

@login_required
def makeart(request):
    return render(request, "makeart.html")

#https://www.geeksforgeeks.org/working-with-datetime-objects-and-timezones-in-python/
##############################################################################
########################## LIVE CHAT AND GAME ROOM ###########################
##############################################################################
@login_required
def games(request):
    url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLGamesForDate"
    nfltz = pytz.timezone('US/Eastern')
    tod = datetime.now(nfltz).date()
    today = tod.strftime("%Y%m%d")
    querystring = {"gameDate":today}
    headers = {
	"x-rapidapi-key": "57106580edmshaf54e7fc6006b35p145d26jsn76b265a565c0",
	"x-rapidapi-host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    respo = response.json()
    gameWeek = respo['body'][0]['gameWeek']
    season = respo['body'][0]['season']
    allgames = []
    for game in respo['body']:
        gamedata = {
            'gameID': game['gameID'],
            'away': game['away'],
            'home': game['home'],
            'teamIDHome': game['teamIDHome'],
            'teamIDAway': game['teamIDAway'],
            'gameTime': game['gameTime']
        }
        allgames.append(gamedata)
    return render(request, "games.html", {'allgames':allgames})


@login_required
def playbyplay(request, gameID):
   #https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl
    return render(request, "playbyplay.html", {'gameID':gameID})

#Still being implemented (in progress)
##############################################################################
########################## LIVE CHAT AND GAME ROOM ###########################
##############################################################################
#https://www.photondesigner.com/articles/instant-messenger?ref=rdjango-instant-messenger
@login_required
def gameschat(request):
    if request.method == 'POST':
        gameID = request.POST.get('gameID')
        return redirect('room',gameID=gameID)
    return render(request, "gameslanding.html")


#https://channels.readthedocs.io/en/stable/tutorial/part_2.html
@login_required
def room(request, gameID):
    return render(request, "chat.html", {'gameID':gameID})


#https://www.photondesigner.com/articles/instant-messenger?ref=rdjango-instant-messenger
@login_required
def message(request: HttpRequest) -> HttpResponse:
    content= request.POST.get("content")
    username = request.session.get("username")

    if content:
        models.Message.objects.create(author=author, content=content)
        return HttpResponse(status=201)
    else:
        return HttpResponse(status=200)

@login_required
async def streamchat(request: HttpRequest) -> StreamingHttpResponse:
    async def eventstream():
        async for message in get_existing_messages():
            yield message

        lastid = await get_last_message_id()

        while True:
            newmessages = models.Message.objects.filter(id__gt=last_id).order_by('created_at').values( 'id','author__name','content')
            async for message in newmessages:
                yield f"data: {json.dumps(message)}\n\n"
                last_id = message['id']
            await asyncio.sleep(2)

    async def getexistingmessages() -> AsyncGenerator:
        messages = models.Message.objects.all().order_by('created_at').values('id','author_name','content')
        async for message in messages:
            yield f"data: {json.dumps(message)}\n\n"
    async def getlastmessageid() -> int:
        last_message = await models.Message.objects.all().alast()
        return last_message.id if last_message else 0

    return StreamingHttpResponse(eventstream(), content_type='text/event-stream')
