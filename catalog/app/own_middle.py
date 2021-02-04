from django.contrib.auth import logout

class TripleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        if request.path == '/orders/':
            if request.session.get('amount'):
                request.session['amount'] += 1
                if request.session['amount'] == 3:
                    logout(request)
            else:
                request.session['amount'] = 1
        # Code to be executed for each request/response after
        # the view is called.

        return response