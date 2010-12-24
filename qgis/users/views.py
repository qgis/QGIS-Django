from django.http import HttpResponse
from users.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
  
def usersMap(theRequest):
  myObjects = QgisUser.objects.all()
  return render_to_response("users_map.html", {'myObjects' : myObjects})


