# python logging support to django logging middleware
import logging

from annoying.functions import get_object_or_None
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from olwidget.fields import EditableLayerField, MapField
from olwidget.widgets import EditableLayer, InfoLayer, InfoMap, Map
from users.forms import *
from users.models import *


def usersMap(theRequest):

    users = []
    myUserCount = QgisUser.objects.all().count()
    myRandomUser = None
    myRandomUsers = QgisUser.objects.exclude(image="").order_by("?")[:1]
    if myRandomUsers.count() > 0:
        myRandomUser = myRandomUsers[0]
    for user in QgisUser.objects.all():
        users.append(
            [user.geometry, render_to_string("user_balloon.html", {"user": user})]
        )

    myMap = InfoMap(users)

    return render_to_response(
        "view_users.html",
        {
            "myMap": myMap,
            "myUserCount": myUserCount,
            "myRandomUser": myRandomUser,
        },
        context_instance=RequestContext(theRequest),
    )


def createUser(theRequest):

    myUserCount = QgisUser.objects.all().count()
    if theRequest.method == "POST":
        myForm = QgisUserForm(theRequest.POST)
        if myForm.is_valid():
            myForm.save()
            return HttpResponseRedirect("/community-map/view_users.html")
        else:
            return render_to_response(
                "create_user_form.html",
                {"myForm": myForm, "myUserCount": myUserCount},
                context_instance=RequestContext(theRequest),
            )
    else:
        myForm = QgisUserForm()
        return render_to_response(
            "create_user_form.html",
            {"myForm": myForm, "myUserCount": myUserCount},
            context_instance=RequestContext(theRequest),
        )


def updateUser(theRequest, theId):
    myUserCount = QgisUser.objects.all().count()
    myUser = get_object_or_404(QgisUser, guid=theId)
    if theRequest.method == "POST":
        myForm = QgisUserForm(theRequest.POST, theRequest.FILES, instance=myUser)
        if myForm.is_valid():
            myForm.save()
            return HttpResponseRedirect("/community-map/view_users.html")
        return render_to_response(
            "update_user_form.html",
            {"myUser": myUser, "myForm": myForm, "myUserCount": myUserCount},
            context_instance=RequestContext(theRequest),
        )
    else:
        myForm = QgisUserForm(instance=myUser)
        return render_to_response(
            "update_user_form.html",
            {"myForm": myForm, "myUserCount": myUserCount},
            context_instance=RequestContext(theRequest),
        )


def emailEditAddress(theRequest):

    if theRequest.method == "POST":
        logging.info(" Form was posted!")
        myForm = EmailForm(theRequest.POST)
        logging.info("Email received from form was: %s" % myForm.data["email"])
        recipient = myForm.data["email"]
        myUser = get_object_or_None(QgisUser, email=recipient)
        logging.info(" User is: %s" % myUser)
        if myForm.is_valid() and myUser:
            logging.info(" User if valid and form is valid")
            domain = Site.objects.get_current().domain
            myLink = "http://%s/community-map/edit/%s" % (domain, myUser.guid)
            subject = "QGIS Community Map: Edit Link Reminder"
            message = (
                """Someone, hopefully you, has asked for a reminder for the
      unique link that will allow you to edit your profile settings on our QGIS
      user's map. To edit your location on our QGIS community map, please
      follow this link %s."""
                % myLink
            )
            message += ""
            sender = mail_from = settings.DEFAULT_FROM_EMAIL

            send_mail(subject, message, sender, [recipient])

            return HttpResponseRedirect("/community-map/edit/email_confirm.html")
        else:
            myUserCount = QgisUser.objects.all().count()
            msg = _("User is NOT valid.")
            messages.warning(theRequest, msg, fail_silently=True)
            logging.info("User or form is NOT valid")
            return render_to_response(
                "update_user.html",
                {"myForm": myForm, "myUserCount": myUserCount},
                context_instance=RequestContext(theRequest),
            )

    else:
        myUserCount = QgisUser.objects.all().count()
        myForm = EmailForm()
        return render_to_response(
            "update_user.html",
            {"myForm": myForm},
            context_instance=RequestContext(theRequest),
        )
