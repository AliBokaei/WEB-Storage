# from django.contrib.auth import login
# from django.contrib.auth.forms import AuthenticationForm
# from django.shortcuts import render, redirect
#
#
# # Create your views here.
# def loginView(request):
#     context = {}
#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             # Login HERE
#             login(request, form.get_user())
#             # print("User :" + "logged in")
#             return redirect('/home/')
#         else:
#             errors = form.errors.items()
#             context2 = {
#                 'errors': errors  # Add the errors to the context
#
#             }
#             return render(request, 'indexErrorLogin.htm', context2)
#
#     else:
#         form = AuthenticationForm()
#
#     return render(request, 'indexLogin.htm', context)


from django.shortcuts import render, redirect
from django.contrib.auth import login, get_backends
from .forms import EmailOrUsernameAuthenticationForm


def loginView(request):
    context = {}
    if request.method == 'POST':
        form = EmailOrUsernameAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']

            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            login(request, user)

            request.session['user_info'] = {
                'username': user.username,
                'email': user.email,
                # and other
            }

            return redirect('/home/')
        else:
            errors = form.errors.items()
            context['errors'] = errors  # Add the errors to the context
            return render(request, 'indexErrorLogin.htm', context)

    else:
        form = EmailOrUsernameAuthenticationForm()

    context['form'] = form  # Make sure form is included in the context
    return render(request, 'indexLogin.htm', context)
