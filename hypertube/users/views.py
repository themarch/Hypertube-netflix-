from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateCheck, UserUpdateForm, ProfileUpdateLanguage, UserUpdateMailForm
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from users.models import Profile
from video.models import Torrent

def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        email_qs = User.objects.filter(email=form.data['email'])
        if email_qs.exists():
            messages.info(request, f'Email already taken')
            return redirect ('register')
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            username = form.cleaned_data.get('username')
            current_site = get_current_site(request)
            mail_subject = 'Activate your Hypertube account.'
            message = render_to_string('users/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, f'Please confirm your email address to complete the registration!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form, 'title': 'Register',})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f'Thank you for your registration, you can now login!')
        return redirect('list')
    else:
        messages.error(request, f'validation link error')
        return redirect('list')
        
@login_required
def profile(request):
     inshalah = request.POST.get('tok')
     if request.method == 'POST' and 'tok' in request.POST:
        name = request.user
        id_profile = User.objects.get(username=name).pk
        token = Profile.objects.get(id=id_profile)
        token.token = ''
        token.save()
     if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        l_form = ProfileUpdateLanguage(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        m_form = UserUpdateMailForm(request.POST, instance=request.user)
        try:
            if len(u_form.data['username']) < 9 or len(u_form.data['username']) > 19:
                messages.info(request, f"Your login must have 9 character at least or 18 max")
                return redirect('profile')
            email_qs = User.objects.filter(email=u_form.data['email'])
            username_qs = User.objects.filter(username=u_form.data['username'])
            username_qs1 = User.objects.filter(username=u_form.data['username']).first()
            language = request.POST.getlist('language')
            if email_qs.exists() and email_qs.first().email != request.user.email:
                messages.info(request, f"Email already taken")
                return redirect('profile')
            if username_qs.exists() and username_qs.first().username != request.user.username:
                messages.info(request, f"Username already exists")
                return redirect('profile')
        except:
            pass
        if u_form.is_valid() and p_form.is_valid() and l_form.is_valid() and m_form.is_valid():
            u_form.save()
            p_form.save()
            l_form.save()
            m_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
     else:
        u_form = UserUpdateCheck(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        l_form = ProfileUpdateLanguage(instance=request.user.profile)
        m_form = UserUpdateMailForm(instance=request.user)

     context = {
        'u_form': u_form,
        'p_form': p_form,
        'l_form': l_form,
        'm_form': m_form,
     }
     return render(request, 'users/profile.html', context)

@login_required
def public_profile(request, id_user):
    try:
        inshalah = request.POST.get('tok')
        if request.method == 'POST' and 'tok' in request.POST:
           name = request.user
           id_profile = User.objects.get(username=name).pk
           token = Profile.objects.get(id=id_profile)
           token.token = ''
           token.save()
        firstname = 0
        lastname = 0
        rien = 0
        super_username = User.objects.filter(id=id_user).first()
        if (super_username == None):
            return redirect('/')
        super_firstname = User.objects.filter(id=id_user).first().first_name
        if (super_firstname == ''):
            firstname = 1
        super_lastname = User.objects.filter(id=id_user).first().last_name
        if (super_lastname == ''):
            lastname = 1
        photo = Profile.objects.filter(id=id_user).first().image
        already = Profile.objects.filter(id=id_user).first().already
        already = already.strip().split(' ')
        tab = []
        for elem in already:
            try:
                tab.append(Torrent.objects.get(id=int(elem)).name)
            except ValueError:
                rien = 1
                pass
        #print(ta)
        photo = str(photo)
        url = '/media/' + photo
        context = {
            'firstname': firstname,
            'lastname': lastname,
            'rien' : rien,
            'film' : tab,
            'super_username': super_username,
            'super_firstname': super_firstname,
            'super_lastname' : super_lastname,
            'photo': url
        }
        return render(request, 'users/public_profile.html', context)
    except AttributeError:
        return redirect ('/')


#C'est moche, mais ca permet que si on ne donne pas d'id
#ca redirige sur l'accueil au lieu de bugger
@login_required
def public_profile_redirect(request):
    return redirect('/')

@login_required
def list_user(request):
    inshalah = request.POST.get('tok')
    if request.method == 'POST' and 'tok' in request.POST:
       name = request.user
       id_profile = User.objects.get(username=name).pk
       token = Profile.objects.get(id=id_profile)
       token.token = ''
       token.save()
    username = User.objects.all()
    nb_id = len(username)
    ind = 1
    tab = []
    while (ind != nb_id + 1):
        tab.append(Profile.objects.get(id=ind).image)
        ind = ind + 1
    context = {
        'tab' : tab,
        'user': username
    }
    return render(request, 'users/list_user.html', context)

def redirect_404(requests):
    return redirect('/')

def error_404(request, exception):
    return render(request,'users/404.html')

def error_500(request):
    return render(request, 'users/404.html')

def error_403(request, exception):
    return render(request, 'users/404.html')