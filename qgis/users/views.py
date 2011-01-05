from django.http import HttpResponse
from users.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from users.forms import *
  
def usersMap(theRequest):
  myObjects = QgisUser.objects.all()
  return render_to_response("view_users.html", {'myObjects' : myObjects}, context_instance=RequestContext(theRequest))

def createUser(theRequest):
  myStartString = """<form action="" method="post" accept-charset="utf-8" class="horizontal">"""
  myEndString   = """<button type="submit">Save</button></form>"""

  if theRequest.method == 'POST':
    myForm = QgisUserForm(theRequest.POST)
    if myForm.is_valid():
       myObject = myForm.save()
       return HttpResponseRedirect("/community-map/view_users.html")
    else:
      myFormAs_p = myStartString + myForm.as_p() + myEndString
      return render_to_response("create_user_form.html", {'myObject' : myFormAs_p}, context_instance=RequestContext(theRequest))

  else:
    myForm = QgisUserForm()
    myFormAs_p = myStartString + myForm.as_p() + myEndString
    return render_to_response("create_user_form.html", {'myObject' : myFormAs_p}, context_instance=RequestContext(theRequest))

