from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.translation import ugettext as _
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.shortcuts import resolve_url
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import render_to_response

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (REDIRECT_FIELD_NAME, login,  
    logout, get_user_model, update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.signals import user_logged_in, user_logged_out



#@csrf_protect
##@never_cache
#def login(request):
#    #template_name='task_list.html'
#    authentication_form=AuthenticationForm
#    """
#    Displays the login form and handles the login action.
#    """
#    form = authentication_form()
#    context = RequestContext(request)
#
#    if request.user.is_superuser or request.user.is_staff:
#        pass
#    if request.method == "POST":
#        form = authentication_form(data=request.POST)
#        if form.is_valid():
#            user = authenticate( username=form.get_user(), \
#                    password=form.cleaned_data['password'])
#            if user is not None:
#                if user.is_active:
#                    login(request, user )
#            return HttpResponseRedirect( reverse("task_list"),)
#            """
#            return render_to_response( template_name, {
#                'form' : form,
#            },context_instance=context )
#            """
#        else:
#            print form.errors
#            error_msg = "Invalid Username / Password."
#            messages.add_message(request, messages.ERROR, error_msg)
#            pass
#
#    return HttpResponseRedirect( reverse("task_list"),)

@csrf_protect
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect( reverse("housekeep:task_list"),)
            # Redirect to a success page.
        else:
            error_msg = "Account disabled"
            messages.add_message(request, messages.ERROR, error_msg)
            # Return a 'disabled account' error message
    else:
        error_msg = "Invalid Username / Password."
        messages.add_message(request, messages.ERROR, error_msg)
        # Return an 'invalid login' error message.


@login_required
def logout_view(request):
    template_name='admin_profile/admin_login.html'
    username = request.user
    success_msg = '%s, You have successfully logged out.'%username
    messages.add_message(request, messages.SUCCESS, success_msg)
    user = getattr(request, 'user', None)
    if hasattr(user, 'is_authenticated') and not user.is_authenticated():
        user = None
    user_logged_out.send(sender=user.__class__, request=request, user=user)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
    return HttpResponseRedirect(reverse("housekeep:task_list"),)


#@login_required
#def logout_view(request):
#    return logout(request)
#    return HttpResponseRedirect(reverse("task_list"),)


'''
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def logout(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    auth_logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)

    if (redirect_field_name in request.POST or
            redirect_field_name in request.GET):
        next_page = request.POST.get(redirect_field_name,
                                     request.GET.get(redirect_field_name))
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': _('Logged out')
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
        current_app=current_app)

'''
