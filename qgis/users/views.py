from django.http import HttpResponse
from users.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from annoying.functions import get_object_or_None
from django.template import RequestContext
from users.forms import *
from olwidget.fields import MapField, EditableLayerField
from olwidget.widgets import Map, EditableLayer, InfoLayer, InfoMap
from django.core.mail import send_mail

from users.models import *
# python logging support to django logging middleware
import logging
  
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
    logging.info (" Form was posted!")
    myForm = EmailForm( theRequest.POST )
    logging.info("Email received from form was: %s" % myForm.data['email'])
    recipient = myForm.data['email']
    myUser = get_object_or_None(QgisUser, email=recipient)
    logging.info (" User is: %s" % myUser)
    if myForm.is_valid() and myUser:
      logging.info(" User if valid and form is valid")
      myLink = "http://users.qgis.org/community-map/edit/" + myUser.guid 
      subject = "QGIS Community Map: Edit Link Reminder"
      message = """Someone, hopefully you, has asked for a reminder for the unique link that will allow you to edit your profile settings on our QGIS user's map. To edit your location on our QGIS community map, please follow this link <a href="%s">%s</a>.""" % (myLink,myLink)
      message += "" 
      sender = "QGIS community website"
         
      send_mail(subject, message, sender, [recipient])
        
      return HttpResponseRedirect("/community-map/edit/email_confirm.html")
    else:
      logging.info(" User or form is NOT valid")
      return render_to_response("update_user.html", {'myForm' : myForm}, context_instance=RequestContext(theRequest))

  else:
    myForm = EmailForm()
    return render_to_response("update_user.html", {'myForm' : myForm}, context_instance=RequestContext(theRequest))        
        
 

