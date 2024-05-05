from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from django.views.generic import View
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django_redis import get_redis_connection
from django.core.paginator import Paginator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages

from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from itsdangerous import SignatureExpired
import re
from bocfx import bocfx
import math

from user.models import User, SenderAddress, ReceiverAddress
from product.models import ProductCategory, ProductSKU
from order.models import OrderInfo, OrderProduct
from utils.mixin import LoginRequiredMixin
from celery_tasks.tasks import sendRegisterActivateEmail, sendReactivateEmail
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox


# Create your views here.
### To perform registration
class RegisterView(View):
    """To display registration page"""

    def get(self, request):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        # To get the product category
        categories = ProductCategory.objects.all()

        return render(request, 'register.html', {'audExRate': audExRate, 'categories': categories})
    
    def post(self, request):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000
        
        ### 1. Receiving data #####################################################################
        username = request.POST.get('userName')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        agreement = request.POST.get('agreement') # user might skip this one


        ### 2. Checking data ######################################################################
        # To check if data are all provided
        if not all([username, password, email]): # exclude "agreement" in case user might skip this one
            
            return render(request, 'register.html', {'audExRate': audExRate, 'errmsg': '数据不完整'})

        # To check if email has correct format
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            
            return render(request, 'register.html', {'audExRate': audExRate, 'errmsg': '邮箱格式不正确'})

        # To check if statement is agreed
        if agreement != 'on':
            
            return render(request, 'register.html', {'audExRate': audExRate, 'errmsg': '请同意协议'})

        # To check if email is used, email is the unique one
        try:
            user = User.objects.get(email=email)
        
        except User.DoesNotExist:
            user = None

        if user:
            return render(request, 'register.html', {'audExRate': audExRate, 'errmsg': '邮箱已使用，请选择新注册邮箱'})


        ### 3. Processing the data ################################################################
        # Create the "user"
        user = User.objects.create_user(username, email, password)

        # Make sure it is not active first
        user.is_active = 0
        user.save()

        # Send activation email, including the activation link
        # activation link needs to include user information, encrypted
        serializer = Serializer(settings.SECRET_KEY)
        info = {'confirm': user.email}
        token = serializer.dumps(info)

        siteProtocol = 'https' if request.is_secure() else 'http'
        siteDomain = get_current_site(request).domain
        
        # Send registration activation email via celery delay queue
        sendRegisterActivateEmail.delay(username, email, token, siteProtocol, siteDomain)

        # Success, return respons and back to Home Page
        return redirect(reverse('product:index'))


### To perform the activation, after user click the activation link from the email sent
class ActivateView(View):
    """Activate User"""

    def get(self, request, token):
        """To activate the user"""

        serializer = Serializer(settings.SECRET_KEY)
        try:
            # To set the expiration timer: 3600s
            info = serializer.loads(token, max_age = 3600)

            # To get the dictionary content: user email
            email = info['confirm']

            # To get the user ID and change is_active status
            user = User.objects.get(email = email)
            user.is_active = 1
            user.save()

            # Redirect back to login page
            return redirect(reverse('user:login'))

        # Throw expiration exception
        except SignatureExpired as e:
            
            # Need to update to complete the registration/activaiton process
            return redirect(reverse('user:activationLinkExpires'))


### To display the link expiration message and setup redirection to "register" page
class ActivationLinkExpiresView(View):

    def get(self, request):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        return render(request, 'activationLinkExpires.html', {'audExRate': audExRate})


### To login the user space, to check if username needs to be memorized by cookies (cookies use Redis)
class LoginView(View):
    """Login"""

    def get(self, request):
        """Login View"""

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        # To check if username is remembered
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        # To get the product category
        categories = ProductCategory.objects.all()


        content = {
            'audExRate': audExRate,
            'username':username,
            'checked':checked,
            'categories': categories,
        }

        return render(request, 'login.html', content)
    

    def post(self, request):
        """Login checking"""

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        ### 1. Receiving data #####################################################################
        username = request.POST.get('username')
        password = request.POST.get('pwd')


        ### 2. Checking data ######################################################################
        if not all([username, password]):
            return render(request, 'login.html', {'audExRate': audExRate, 'errmsg': '请输入密码'})
    
        # Using Django internal function to authenticate user information
        user = authenticate(username=username, password=password)
        if user is not None:
            # A backend authenticated the credentials
            if user.is_active:
                # To record the login status
                login(request, user)

                # To get the redirection address after the login
                # Default is homepage
                next_url = request.GET.get('next', reverse('product:index'))

                # HttpResponseRedirect to the homepage
                response = redirect(next_url)

                # To check if needs to remember the username
                remember = request.POST.get('remember')

                if remember == 'on':
                    # username is remembered
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                
                # Redirect back to homepage
                return response

            else:
                # The password is valid, but the account is not activated
                return render(request, 'login.html', {'audExRate': audExRate, 'errmsg': '请激活账户'})
        
        else:
            # No backend authenticated the credentials
            return render(request, 'login.html', {'audExRate': audExRate, 'errmsg': '用户名或者密码错误'})


### To logout the user space
class LogoutView(View):
    """Log out"""

    def get(self, request):
        """Log out"""
        # django function logout will clear all the user session information
        logout(request)

        return redirect(reverse('product:index'))


### To reset password if user forgets
class PasswordResetView(View):
    """Help user to recover the password"""

    def get(self, request):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000
        
        # To get the product category
        categories = ProductCategory.objects.all()

        return render(request, 'passwordReset.html', {'audExRate': audExRate, 'categories': categories})

    def post(self, request):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        ### 1. Receiving data #####################################################################
        email = request.POST.get('email')


        ### 2. Checking data ######################################################################
        # To check if email has correct format
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'passwordReset.html', {'audExRate': audExRate, 'errmsg': '邮箱格式不正确'})

        # To check if email is used
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'register.html', {'audExRate': audExRate, 'errmsg': '邮箱并没有注册，请重新注册'})


        ### 3. Processing the data ################################################################
        serializer = Serializer(settings.SECRET_KEY)
        accountReactivationToken = PasswordResetTokenGenerator().make_token(user)
        info = {'reactivationToken': accountReactivationToken, 'userId': user.id, 'lastLogin': user.last_login.isoformat()}
        token = serializer.dumps(info)

        siteProtocol = 'https' if request.is_secure() else 'http'
        siteDomain = get_current_site(request).domain

        # Send registration activation email via celery delay queue
        sendReactivateEmail.delay(user.username, user.email, token, siteProtocol, siteDomain)

        # Success, return respons and back to Home Page
        return redirect(reverse('user:login'))


### To proceed the password reset
class PasswordResetConfirmView(View):

    def get(self, request, token):
        """To reset the password for user"""

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        serializer = Serializer(settings.SECRET_KEY)
        try:
            # To set the expiration timer: 3600s
            info = serializer.loads(token, max_age = 3600)

            # To get the dictionary content: user email
            reactivationToken = info['reactivationToken']
            userId = info['userId']
            lastLogin = info['lastLogin']

            # To get the user ID and change is_active status
            try:
                user = User.objects.get(id=userId)
            except:
                user = None

            if user is not None and PasswordResetTokenGenerator().check_token(user, reactivationToken):
                
                form = SetPasswordForm(user)
                return render(request, 'passwordResetConfirm.html', {'audExRate': audExRate, 'form': form})

            else:

                # Redirect back to register page
                return redirect(reverse('user:register'))

        # Throw expiration exception
        except SignatureExpired as e:

            # Need to update to complete the registration/activaiton process
            return redirect(reverse('user:passwordResetLinkExpires'))


    def post(self, request, token):

        serializer = Serializer(settings.SECRET_KEY)
        try:
            # To set the expiration timer: 3600s
            info = serializer.loads(token, max_age = 3600)
            # To get the dictionary content: user email
            reactivationToken = info['reactivationToken']
            userId = info['userId']
            lastLogin = info['lastLogin']

            # To get the user ID and change is_active status
            try:
                user = User.objects.get(id=userId)
            except:
                user = None

            if user is not None and PasswordResetTokenGenerator().check_token(user, reactivationToken):
                
                print(user)

                form = SetPasswordForm(user, request.POST)
                print(form.is_valid())

                if form.is_valid():
                    form.save()

                    # To the "Done" page to show user password reset is successful
                    return redirect(reverse('user:passwordResetSuccess'))
                
                else:
                    for error in list(form.errors.values()):
                        messages.error(request, error)

                    return redirect(reverse('user:passwordResetFail'))

            else:
                
                # Redirect back to register page
                return redirect(reverse('user:passwordResetFail'))

        # Throw expiration exception
        except SignatureExpired as e:

            # Need to update to complete the registration/activaiton process
            return redirect(reverse('user:passwordResetLinkExpires'))


### To display the link expiration message and setup redirection to "password reset" page
class PasswordResetLinkExpiresView(View):

    def get(self, request):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        return render(request, 'passwordResetLinkExpires.html', {'audExRate': audExRate})


### To display the password reset success message and setup redirection to "login" page
class PasswordResetSuccessView(View):

    def get(self, request):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        return render(request, 'passwordResetSuccess.html', {'audExRate': audExRate})


### To display the password reset fail message and setup redirection to "register" page
class PasswordResetFailView(View):

    def get(self, request):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        return render(request, 'passwordResetFail.html', {'audExRate': audExRate})


### To show "user information" and recent browsing history View
class UserInfoView(LoginRequiredMixin, View):
    """User Center - Information"""

    def get(self, request):
        """Display"""
        # page = 'user'
        # request.user
        # 1. if current user is NOT login, an instance of AnonymousUser (request.user.is_authenticated = False)
        # 2. if current user is login, an instance of User (request.user.is_authenticated = True)
        # django can also pass request.user information to the template

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        # To get the login user information
        user = request.user
        senderAddress = SenderAddress.objects.getDefaultAddress(user)

        # To show user browsing history
        con = get_redis_connection('default')

        historyKey = 'history_%d' % user.id
        skuIds = con.lrange(historyKey, 0, 4)

        # To get the product information as per sku IDs
        productList = [ProductSKU.objects.get(id=productId) for productId in skuIds]

        # To get the product category
        categories = ProductCategory.objects.all()


        # To summarize the return message
        context = {
            'audExRate': audExRate,
            'categories': categories,
            'page': 'user',
            'senderAddress': senderAddress,
            'productList': productList
        }

        return render(request, 'userCenterInfo.html', context)


### To show "user order information", with pagination
class UserOrderView(LoginRequiredMixin, View):
    """User Center - Order List"""

    def get(self, request, page):
        """Display"""

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000
        
        user = request.user

        # To get user order information
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        for order in orders:

            orderSkus = OrderProduct.objects.filter(order=order.orderId)

            for orderSku in orderSkus:

                # To calculate the subtotal of each product (sku)
                skuAmount = orderSku.skuCount * orderSku.skuPrice
                orderSku.skuAmount = skuAmount

            # To associate order status and production information to each order
            order.paymentMethodName = OrderInfo.PAYMENT_METHODS[order.paymentMethod]
            order.statusName = OrderInfo.ORDER_STATUS[order.orderStatus]
            order.orderSkus = orderSkus

        # To do pagination, "x" order per page
        ordersPerPage = 2
        paginator = Paginator(orders, ordersPerPage)


        # To get the content of page "#""
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # To get the contents on page "page"
        ordersPage = paginator.page(page)

        for order in ordersPage:
            for sku in order.orderSkus:
                sku.skuPrice = math.ceil(float(sku.skuPrice) * 10) / 10
                sku.skuPriceCN = math.ceil(float(sku.skuPrice) * audExRate * 10) / 10

            order.totalSkuPrice = math.ceil(float(order.totalSkuPrice) * 10) / 10
            order.totalSkuPriceCN = math.ceil(float(order.totalSkuPrice) * audExRate * 10) / 10

            order.totalServicePrice = math.ceil(float(order.totalServicePrice) * 10) / 10
            order.totalServicePriceCN = math.ceil(float(order.totalServicePrice) * audExRate * 10) / 10

            order.totalLogisticsPrice = math.ceil(float(order.totalLogisticsPrice) * 10) / 10
            order.totalLogisticsPriceCN = math.ceil(float(order.totalLogisticsPrice) * audExRate * 10) / 10

            order.totalHandlingFee = math.ceil(float(order.totalHandlingFee) * 10) / 10
            order.totalHandlingFeeCN = math.ceil(float(order.totalHandlingFee) * audExRate * 10) / 10

            order.totalPrice = math.ceil(float(order.totalPrice) * 10) / 10
            order.totalPriceCN = math.ceil(float(order.totalPrice) * audExRate * 10) / 10

        # To limit the display of page number to "5"
        # 1. If total less than 5, then just display [1 - page number]
        # 2. If current is on page 3，then display [1,2,3,4,5]
        # If current is on last 3 pages, then display [4,5,6,7,8] num_pages-4 to num_oages+1
        numPages = paginator.num_pages

        # 1 Total pages less than 5, to show all
        if numPages < 5:
            pages = range(1, numPages + 1)

        # 2 
        elif page <= 3:
            pages = range(1, 6)
        
        elif numPages - page <= 2:
            pages = range(numPages-4, numPages+1)
        
        else:
            pages = range(page-2, page+3)
            

        context = {
            'audExRate': audExRate,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'SUPAY_REDIRECT_DOMAIN': settings.SUPAY_REDIRECT_DOMAIN,
            'WECHATPAY_URL': settings.WECHATPAY_URL,
            'ALIPAY_URL': settings.ALIPAY_URL,
            'MERCHANT_ID': settings.MERCHANT_ID,
            'AUTHENTICATION_CODE': settings.AUTHENTICATION_CODE,
            'ordersPage': ordersPage,
            'page': 'order',
            'pages': pages,
        }

        return render(request, 'userCenterOrder.html', context)


### To show "sender address addition and address book update" interface
class SenderAddressView(LoginRequiredMixin, View):

    def get(self, request):
        """Display"""

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        # To get the login user information
        user = request.user

        # To get the user delivery address
        senderAddresses = SenderAddress.objects.all()

        # To get the product category
        categories = ProductCategory.objects.all()

        # To summarize the response 
        context = {
            'audExRate': audExRate,
            'categories': categories,
            'page': 'senderAddress', 
            'senderAddresses': senderAddresses
            }


        return render(request, 'userCenterSenderAddress.html', context)
    
    def post(self, request):
        """User Center - To update or add sender address"""
        # 1. updateSenderAddress
        # 2. newSenderAddress

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        if 'updateSenderAddress' in request.POST:

            # To initialize all to be "False"
            SenderAddress.objects.update(isDefault=False)

            # To set the one with senderAddressId to be "True"
            for key, value in request.POST.items():
                if key.isdigit():

                    instance = SenderAddress.objects.get(id=key)
                    instance.isDefault = True
                    instance.save()

            # Return back to the address page (GET method is triggered to load the page)
            return redirect(reverse('user:senderAddress'))

        elif 'newSenderAddress' in request.POST:
            ### 1. Receiving data #####################################################################
            # To get the user delivery address
            senderAddresses = SenderAddress.objects.all()

            # To get the product category
            categories = ProductCategory.objects.all()

            # To get the parameters from UI
            sender = request.POST.get('sender')
            senderAddr = request.POST.get('senderAddr')
            senderTel = request.POST.get('senderTel')

            ### 2. Checking data ######################################################################
            if not all([sender, senderAddr, senderTel]):
                # To construct the response 
                context = {
                    'audExRate': audExRate,
                    'categories': categories,
                    'page': 'senderAddress', 
                    'senderAddresses': senderAddresses,
                    'errmsg': '数据不完整'
                    }

                return render(request, 'userCenterSenderAddress.html', context)
            
            if not re.match(r'^(?:04\d{8}|1[3-9]\d{9})$', senderTel):
                # To construct the response 
                context = {
                    'audExRate': audExRate,
                    'categories': categories,
                    'page': 'senderAddress', 
                    'senderAddresses': senderAddresses,
                    'errmsg': '手机格式不正确'
                    }

                return render(request, 'userCenterSenderAddress.html', context)
            

            ### 3. Processing the data ################################################################
            # If user already has receiving addresses, the newly added one will be set 
            # as the default address and those existing ones will be set as non default.

            # To get the login user information
            user = request.user

            # To check if user has default address,
            senderAddresses = SenderAddress.objects.all()

            if senderAddresses:
                for objSenderAddress in senderAddresses:
                    objSenderAddress.isDefault = False
                    objSenderAddress.save()
                
            # To add the address and set it to be default
            SenderAddress.objects.create(user = user,
                                         sender = sender,
                                         senderAddr = senderAddr,
                                         senderTel = senderTel,
                                         isDefault = True)


            ### 4. Return back to the address page (GET method is triggered to load the page)
            return redirect(reverse('user:senderAddress'))


### To show "receiver address addition and address book update" interface
class ReceiverAddressView(LoginRequiredMixin, View):
    """User Center - Receiver Address List"""
    
    def get(self, request):
        """Display"""

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        # To get the login user information
        user = request.user
        
        # To get the user delivery address
        receiverAddresses = ReceiverAddress.objects.all()

        # To get the product category
        categories = ProductCategory.objects.all()

        # To summarize the response 
        context = {
            'audExRate': audExRate,
            'categories': categories,
            'page': 'receiverAddress', 
            'receiverAddresses': receiverAddresses
            }

        return render(request, 'userCenterReceiverAddress.html', context)

    def post(self, request):
        """User Center - To update or add receiver address"""
        # 1. updateReceiverAddress
        # 2. newReceiverAddress

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        if 'updateReceiverAddress' in request.POST:
            
            # To initialize all to be "False"
            ReceiverAddress.objects.update(isDefault=False)

            # To set the one with senderAddressId to be "True"
            for key, value in request.POST.items():
                if key.isdigit():

                    instance = ReceiverAddress.objects.get(id=key)
                    instance.isDefault = True
                    instance.save()
            
            # Return back to the current address page (GET method is triggered to load the page)
            return redirect(reverse('user:receiverAddress'))

        
        elif 'newReceiverAddress' in request.POST:
            ### 1. Receiving data #####################################################################
            # To get the user delivery address
            receiverAddresses = ReceiverAddress.objects.all()

            # To get the product category
            categories = ProductCategory.objects.all()

            # To get the parameters from UI
            receiver = request.POST.get('receiver')
            receiverAddr = request.POST.get('receiverAddr')
            receiverTel = request.POST.get('receiverTel')
            
            try:
                receiverIdImageFront = request.FILES['receiverIdImageFront']
            except:
                receiverIdImageFront = '请上传身份证正面图片'

            try:
                receiverIdImageBack = request.FILES['receiverIdImageBack']
            except:
                receiverIdImageBack = '请上传身份证背面图片'

            ### 2. Checking data ######################################################################
            if not all([receiver, receiverAddr, receiverTel]):
                context = {
                    'audExRate': audExRate,
                    'categories': categories,
                    'page': 'receiverAddress', 
                    'receiverAddresses': receiverAddresses,
                    'errmsg': '数据不完整'
                    }
                return render(request, 'userCenterReceiverAddress.html', context)
            
            if not re.match(r'^1[3-9]\d{9}$', receiverTel):
                context = {
                    'audExRate': audExRate,
                    'categories': categories,
                    'page': 'receiverAddress', 
                    'receiverAddresses': receiverAddresses,
                    'errmsg': '手机格式不正确'
                    }
                return render(request, 'userCenterReceiverAddress.html', context)
            

            ### 3. Processing the data ################################################################
            # If user already has receiving addresses, the newly added one will be set 
            # as the default address and those existing ones will be set as non default.

            # To get the login user information
            user = request.user

            # To check if user has default address,
            receiverAddresses = ReceiverAddress.objects.all()

            if receiverAddresses:
                for objReceiverAddresses in receiverAddresses:
                    objReceiverAddresses.isDefault = False
                    objReceiverAddresses.save()
                
            # To add the address and set it to be default
            ReceiverAddress.objects.create(user = user,
                                           receiver = receiver,
                                           receiverAddr = receiverAddr,
                                           receiverTel = receiverTel,
                                           receiverIdImageFront = receiverIdImageFront,
                                           receiverIdImageBack = receiverIdImageBack,
                                           isDefault = True)


            ### 4. Return back to the address page (GET method is triggered to load the page)
            return redirect(reverse('user:receiverAddress'))


### To show "sender address deletion" interface
class SenderAddressDeleteView(LoginRequiredMixin, View):
     """To delete the record in address book"""
     
     def post(self, request):
    
        ### 1. Receiving data #####################################################################
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        
        senderAddressId = request.POST.get('senderAddressId')
        
        ### 2. Checking and processing data #######################################################
        if not senderAddressId:
            return JsonResponse({'res': 1, 'errmsg': '无效的地址id'})

        try:
            sender = SenderAddress.objects.get(id=senderAddressId)
            sender.delete()
            return JsonResponse({'res': 2, 'message': '删除成功'})

        except SenderAddress.DoesNotExist as e:
            return JsonResponse({'res': 3, 'errmsg': '地址待补充'})
        

### To show "receiver address deletion" interface
class ReceiverAddressDeleteView(LoginRequiredMixin, View):
     """To delete the record in address book"""
     
     def post(self, request):
    
        ### 1. Receiving data #####################################################################
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        
        receiverAddressId = request.POST.get('receiverAddressId')
        
        ### 2. Checking and processing data #######################################################
        if not receiverAddressId:
            return JsonResponse({'res': 1, 'errmsg': '无效的地址id'})

        try:
            receiver = ReceiverAddress.objects.get(id=receiverAddressId)
            receiver.delete()
            return JsonResponse({'res': 2, 'message': '删除成功'})

        except ReceiverAddress.DoesNotExist as e:
            return JsonResponse({'res': 3, 'errmsg': '地址待补充'})

