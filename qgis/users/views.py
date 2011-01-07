from django.http import HttpResponse
from users.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from users.forms import *
from olwidget.fields import MapField, EditableLayerField
from olwidget.widgets import Map, EditableLayer, InfoLayer, InfoMap
from django.core.mail import send_mail

from users.models import *
  
def usersMap(theRequest):
  myObjects = QgisUser.objects.all()
  return render_to_response("view_users.html", {'myObjects' : myObjects}, context_instance=RequestContext(theRequest))

def createUser(theRequest):

  if theRequest.method == 'POST':
    myForm = QgisUserForm(theRequest.POST)
    if myForm.is_valid():
       myForm.save()
       return HttpResponseRedirect("/community-map/view_users.html")
    else:
       return render_to_response("create_user_form.html", {'myForm' : myForm}, context_instance=RequestContext(theRequest))
  else:
    myForm = QgisUserForm()
    return render_to_response("create_user_form.html", {'myForm' : myForm}, context_instance=RequestContext(theRequest))
    

def updateUser(theRequest, theId):
  myUser = get_object_or_404(QgisUser,guid=theId)
  if theRequest.method == 'POST':
    myForm = QgisUserForm(theRequest.POST, instance=myUser)
    if myForm.is_valid():
        myForm.save()
        return HttpResponseRedirect("/community-map/view_users.html")
    return render_to_response("update_user_form.html", {
            'myUser': myUser, 'myForm': myForm,
        }, context_instance=RequestContext(request))
  else:
    myForm = QgisUserForm(instance=myUser)
    return render_to_response("update_user_form.html", {'myForm' : myForm}, context_instance=RequestContext(theRequest))
    
def emailEditAddress(theRequest):
  
  if theRequest.method == 'POST':
    myForm = EmailForm(theRequest.POST)
    if myForm.is_valid():
     subject = "QGIS Community Map: update user"
     message = "Please follow this link: http:/localhost:8000/community-map/edit/"
     message += "" 
     sender = "QGIS community website"
     recipient = form.cleaned_data['email']
        
     send_mail(subject, message, sender, recipient)
       
     return HttpResponseRedirect("/community-map/edit/email_confirm.html")
    else:
       return render_to_response("update_user.html", {'myForm' : myForm}, context_instance=RequestContext(theRequest))

  else:
    myForm = EmailForm()
    return render_to_response("update_user.html", {'myForm' : myForm}, context_instance=RequestContext(theRequest))        
        
 

