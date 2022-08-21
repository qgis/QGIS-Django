from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from annoying.functions import get_object_or_None
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings
from users.forms import *
from users.models import *
from olwidget.fields import MapField, EditableLayerField
from olwidget.widgets import Map, EditableLayer, InfoLayer, InfoMap

import os
# python logging support to django logging middleware
import logging

def usersMap(theRequest):

  users = []
  myUserCount = QgisUser.objects.all().count()
  myRandomUser = None
  myRandomUsers = QgisUser.objects.exclude(image="").order_by('?')[:1]
  if myRandomUsers.count() > 0:
    myRandomUser = myRandomUsers[0]
  for user in QgisUser.objects.all():
      users.append([user.geometry, render_to_string('user_balloon.html', {'user' : user})])

  myMap = InfoMap(users)

  return render(
      theRequest,
      "view_users.html",
      {
        'myMap' : myMap,
        'myUserCount' : myUserCount,
        'myRandomUser' : myRandomUser,
      },
      context_instance=RequestContext(theRequest))

def createUser(theRequest):

  myUserCount = QgisUser.objects.all().count()
  if theRequest.method == 'POST':
    myForm = QgisUserForm(theRequest.POST)
    if myForm.is_valid():
       myForm.save()
       return HttpResponseRedirect("/community-map/view_users.html")
    else:
       return render(theRequest, "create_user_form.html", {'myForm' : myForm, 'myUserCount' : myUserCount },
           context_instance=RequestContext(theRequest))
  else:
    myForm = QgisUserForm()
    return render(theRequest, "create_user_form.html", {'myForm' : myForm, 'myUserCount' : myUserCount },
        context_instance=RequestContext(theRequest))


def updateUser(theRequest, theId):
  myUserCount = QgisUser.objects.all().count()
  myUser = get_object_or_404(QgisUser,guid=theId)
  if theRequest.method == 'POST':
    myForm = QgisUserForm(theRequest.POST, theRequest.FILES, instance=myUser)
    if myForm.is_valid():
        myForm.save()
        return HttpResponseRedirect("/community-map/view_users.html")
    return render(theRequest, "update_user_form.html", {
            'myUser': myUser, 'myForm': myForm, 'myUserCount' : myUserCount
        }, context_instance=RequestContext(theRequest))
  else:
    myForm = QgisUserForm(instance=myUser)
    return render(theRequest, "update_user_form.html", {'myForm' : myForm, 'myUserCount' : myUserCount},
        context_instance=RequestContext(theRequest))

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
      domain = Site.objects.get_current().domain
      myLink = "http://%s/community-map/edit/%s" % (domain, myUser.guid)
      subject = "QGIS Community Map: Edit Link Reminder"
      message = """Someone, hopefully you, has asked for a reminder for the
      unique link that will allow you to edit your profile settings on our QGIS
      user's map. To edit your location on our QGIS community map, please
      follow this link %s.""" % myLink
      message += ""
      sender =  mail_from = settings.DEFAULT_FROM_EMAIL

      send_mail(subject, message, sender, [recipient])

      return HttpResponseRedirect("/community-map/edit/email_confirm.html")
    else:
      myUserCount = QgisUser.objects.all().count()
      msg = _("User is NOT valid.")
      messages.warning(theRequest, msg, fail_silently=True)
      logging.info("User or form is NOT valid")
      return render(theRequest, "update_user.html", {'myForm' : myForm, 'myUserCount' : myUserCount},
          context_instance=RequestContext(theRequest))

  else:
    myUserCount = QgisUser.objects.all().count()
    myForm = EmailForm()
    return render(theRequest, "update_user.html", {'myForm' : myForm},
        context_instance=RequestContext(theRequest))
