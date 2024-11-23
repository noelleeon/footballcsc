from django.shortcuts import render, HttpResponse
from django.http import HttpResponse
from django.template import loader
from django import template
from dotenv import load_dotenv
from openai import OpenAI
import openai
from channels.routing import ProtocolTypeRouter
import os

#https://www.geeksforgeeks.org/using-python-environment-variables-with-python-dotenv/
load_dotenv()
print(os.getenv("OPEN_API_KEY"))
#https://github.com/Kouidersif/openai-API/blob/main/openapp/views.py
#https://www.geeksforgeeks.org/openai-python-api/
client = OpenAI(api_key=os.environ.get("OPEN_API_KEY"))

#https://stackoverflow.com/questions/1070398/how-to-assign-a-value-to-a-variable-in-a-django-template
register = template.Library()

def fbapp(request):
  return render(request, "myfirst.html")

#https://community.openai.com/t/questions-about-assistant-threads/485239
#Provided from code section of the openAI project
#https://platform.openai.com/docs/overview?lang=python
def searchnav(request):
  if request.method == 'POST':
    print(request.POST)
    question = request.POST.get("question")
    print(question)
    try:
      completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
          {"role":"system","content":"You are a helpful assistant who answers only questions about American football, anything ranging to players, news, teams, history, or statistics. You talk like an American football coach who talks a lot of smack. If someone asks you about anything other than American football you tell them to get lost."},
          {"role":"user","content":question}]
        )
      answer = completion.choices[0].message
    except Exception as e:
      answer = f"an error occured: {str(e)}"
  else:
    answer = None

  return render(request, "searchnav.html", {'answer':answer})

def dash(request):
  return render(request, "dashboard.html")

def profile(request):
  return render(request, "profile.html")

def statistics(request):
  return render(request, "statistics.html")

def stat(request):
  return render(request, "stat.html")

def news(request):
  return render(request, "news.html")

def article(request):
  return render(request, "article.html")

def makeart(request):
  return render(request, "makeart.html")

#https://channels.readthedocs.io/en/stable/tutorial/part_2.html
def livechat(request):
  return render(request, "chat/livechat.html")

def room(request, room_name):
  return render(request, "chat/room.html", {"room_name": room_name})
