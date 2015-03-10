# -*- coding: utf-8 -*-
from social_auth.middleware import SocialAuthExceptionMiddleware
from social_auth.exceptions import AuthFailed
from django.contrib import messages

class CustomSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def get_message(self, request, exception):
        msg = None
        if (isinstance(exception, AuthFailed) and
            exception.message == u"User not allowed"):
            msg =   u"Not in whitelist"
        else:
            msg =   u"Some other problem"
        messages.add_message(request, messages.ERROR, msg)

class LastVisitedMiddleware(object):
    """This middleware sets the last visited url as session field"""

    def process_request(self, request):
        """Intercept the request and add the current path to it"""
        request_path = request.get_full_path()
        try:
            request.session['last_visited'] = request.session['currently_visiting']
        except KeyError:
            # silence the exception - this is the users first request
            pass

        request.session['currently_visiting'] = request_path

    def process_response(self,request, response):
        if response.status_code == 200:
            request.session['previous_url'] = request.get_full_path()
        return response


