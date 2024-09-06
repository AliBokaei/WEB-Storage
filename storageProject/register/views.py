from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib import messages
from .tokens import account_activation_token
from django.contrib.auth import get_backends
from .forms import CustomUserCreationForm

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Your account has been activated")
        return redirect('login.htm')
    else:
        messages.error(request, "Activation link is invalid")

    return render(request, 'activation_invalid.html')

def activationEmail(request, user, to_email, form):
    mail_subject = 'Activate your user account.'
    message = render_to_string("active_acc.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    try:
        email.send(fail_silently=False)
        context = {
            'email': to_email
        }
        user.is_active = True
        user.save()
        return render(request, 'indexEmailSent.htm', context)
    except Exception as e:
        errors = form.errors.items()
        print(f"Error sending email: {e}")
        context = {
            'errors': errors,
            'email_error': str(e)
        }
        return render(request, 'indexError.htm', context)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # activationEmail(request, user, form.cleaned_data.get('email'), form)

            if activationEmail(request, user, form.cleaned_data.get('email'), form):
                return render(request, 'indexEmailSent.htm')
            else:
                user.delete()

            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'

            login(request, user)
            return render(request, 'indexEmailSent.htm')
        else:
            errors = form.errors.items()
            context = {
                'errors': errors,
                'form': form
            }
            return render(request, 'indexError.htm', context)
    else:
        form = CustomUserCreationForm()

    return render(request, 'index.htm', {'form': form})


