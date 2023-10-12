from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

#resetpassword generators

from django.contrib.auth.tokens import PasswordResetTokenGenerator

# to activate account
from django.contrib.sites.shortcuts import get_current_site 
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.urls import NoReverseMatch,reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str,DjangoUnicodeDecodeError

# getting token from utils.py
from .utils import TokenGenerator,generate_token    

# emails
from django.core.mail import send_mail,EmailMultiAlternatives
from django.core.mail import BadHeaderError,send_mail
from django .conf import settings
from django.core.mail import EmailMessage

# threading
import threading


class EmailThread(threading.Thread):
    
    def __init__(self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)
        
    def run(self):
       self.email_message.send()
       
       

def signup(request):
     if request.method=="POST":
        email=request.POST['email']
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'auth/signup.html')
        
        try:
            if User.objects.get(username=email):
                messages.warning(request,"Email is Already Taken")
                return render(request,'auth/signup.html')
        except Exception as identifier:
            pass
        
        user = User.objects.create_user(email,email,password)
        user.save()
        current_site = get_current_site(request)
        email_subject = "Activate your Account"
        message = render_to_string('auth/activate.html',{
            'user':user,
            'domain':'192.168.29.100',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)
        })
        
        email_messages = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
        EmailThread(email_messages).start()
        messages.info(request," Activate your account by clicking the link on your email ")
        return redirect('login')
     return render(request,'auth/signup.html')
    

class ActivateAccountView(View):
    
    def get(self,request,uidb64,token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as identifier:
            user = None
        if user is not None and generate_token.check_token(user,token):
            user.is_active = True
            user.save()
            messages.info(request,"Account activateed Succesfully")
            return redirect('login')
        return render(request,'auth/activatefail.html')
            

def user_login(request):
    if request.method=="POST":
        username=request.POST['email']
        userpassword=request.POST['pass1']
        user=authenticate(username=username,password=userpassword)
        if user is not None:
            login(request,user)
            messages.success(request,"Login Success")
            return render(request,'index.html')

        else:
            messages.error(request,"Invalid Credentials")
            return redirect('login')
    return render(request,'auth/login.html')


def user_logout(request):
    logout(request)
    messages.success(request,"Logout Success")
    return redirect('login')


class ResetEmailView(View):
    
    def get(self,request):
        return render(request,'auth/request_password.html')
    
    def post(self,request):
        email = request.POST['email']
        user = User.objects.filter(email=email)
        
        if user.exists():
            current_site = get_current_site(request)
            email_subject = '[Reset the Password]'
            message = render_to_string('auth/reset_password.html',
            {
                'domain':'192.168.29.100',
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token':PasswordResetTokenGenerator().make_token(user[0])
             })
            
            email_message = EmailMessage(email_subject,messages,settings.EMAIL_HOST_USER,[email])
            EmailThread(email_message).start()
            
            messages.info(request,"WE HAVE SENT YOU AN EMAIL WITH INSTRUCTIONS ON HOW TO RESET THE PASSWORD")
            return render(request,'auth/request_password.html')

class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            
            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset Link is Invalid")
                return render(request,'auth/request_password.html')
        
        except DjangoUnicodeDecodeError as identifier:
            pass
        return render(request,'auth/set-new-password.html',context)
    
    def post(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'auth/set-new-password.html',context)
        
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,"Password Reset Succes Please Login with New Password")
            return redirect('login')
        
        except DjangoUnicodeDecodeError as identifier:
            messages.error(request,"Something went Wrong")
        
        return render(request,'auth/set-new-password.html',context)
