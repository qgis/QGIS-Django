from django.http import HttpResponse
from users.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from users.forms import *
from olwidget.fields import MapField, EditableLayerField
from olwidget.widgets import Map, EditableLayer, InfoLayer, InfoMap

from users.models import *
  
def usersMap(theRequest):
  myObjects = QgisUser.objects.all()
  return render_to_response("view_users.html", {'myObjects' : myObjects}, context_instance=RequestContext(theRequest))

def createUser(theRequest):

  if theRequest.method == 'POST':
    myForm = QgisUserForm(theRequest.POST)
    if myForm.is_valid():
       myObject = myForm.save()
       return HttpResponseRedirect("/community-map/view_users.html")
    else:
       return render_to_response("create_user_form.html", {'myObject' : myForm}, context_instance=RequestContext(theRequest))

  else:
    myForm = QgisUserForm()
    return render_to_response("create_user_form.html", {'myObject' : myForm}, context_instance=RequestContext(theRequest))
    

def updateUser(theRequest, theUser):

  if theRequest.method == 'POST':
    myForm = QgisUserForm(theRequest.POST)
    if myForm.is_valid():
       myObject = myForm.save()
       return HttpResponseRedirect("/community-map/view_users.html")
    else:
       return render_to_response("create_user_form.html", {'myObject' : myForm}, context_instance=RequestContext(theRequest))

  else:
    myForm = QgisUserForm()
    return render_to_response("create_user_form.html", {'myObject' : myForm}, context_instance=RequestContext(theRequest))

