from celery import Celery
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import loader
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.templatetags.static import static
import json

#######################################################################################################################
### To initialise the Django setting environment for Celery to run 
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auking.settings')
django.setup()
#######################################################################################################################

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
@app.task
def sendRegisterActivateEmail(username, toEmail, token, siteProtocol, siteDomain):
    """To send activation email"""
    
    # To send email
    subject = '欢迎您注册爱优品礼品店'
    sender = settings.EMAIL_HOST_USER
    receiver = [toEmail]

    # To construct the html context
    context = {
        'aukingLogoImageURL': static('images/aukingLogo.png'),
        'protocol': siteProtocol,
        'domain': siteDomain,
        'username': username,
        'token': token,
    }

    htmlMessage = render_to_string('emailRegistration.html', context)
    plainMessage = strip_tags(htmlMessage)

    # To perform the send action
    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=plainMessage,
            from_email=sender,
            to=receiver
        )

        message.attach_alternative(htmlMessage, "text/html")
        message.send()

    except Exception as e:
        print(e)



@app.task
def sendReactivateEmail(username, toEmail, token, siteProtocol, siteDomain):
    """To send activation email"""
    
    # To send email
    subject = '找回密码'
    sender = settings.EMAIL_HOST_USER
    receiver = [toEmail]

    # To construct the html context
    context = {
        'aukingLogoImageURL': static('images/aukingLogo.png'),
        'protocol': siteProtocol,
        'domain': siteDomain,
        'username': username,
        'token': token,
    }

    htmlMessage = render_to_string('emailReactivation.html', context)
    plainMessage = strip_tags(htmlMessage)

    # To perform the send action
    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=plainMessage,
            from_email=sender,
            to=receiver
        )

        message.attach_alternative(htmlMessage, "text/html")
        message.send()

    except Exception as e:
        print(e)



#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
from order.models import OrderInfo, OrderProduct

@app.task
def sendPaymentSuccessEmail(toEmail, orderId):
    """To send payment confirmation email"""
    
    # Send email
    subject = '欢迎光临爱优品礼品店'
    sender = settings.EMAIL_HOST_USER
    receiver = [toEmail]

    orderInfo = OrderInfo.objects.get(orderId=orderId)
    orderSkus = OrderProduct.objects.filter(order=orderInfo.orderId)

    for orderSku in orderSkus:

        # To calculate the subtotal of each product (sku)
        skuAmount = orderSku.skuCount * orderSku.skuPrice
        orderSku.skuAmount = skuAmount

    # To associate order status and production information to each order
    orderInfo.paymentMethodName = OrderInfo.PAYMENT_METHODS[orderInfo.paymentMethod]
    orderInfo.statusName = OrderInfo.ORDER_STATUS[orderInfo.orderStatus]
    orderInfo.orderSkus = orderSkus

    context = {
            'aukingLogoImageURL': static('images/aukingLogo.png'),
            'order': orderInfo,
        }

    htmlMessage = render_to_string('emailPaymentSuccess.html', context)
    plainMessage = strip_tags(htmlMessage)

    # To perform the send action
    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=plainMessage,
            from_email=sender,
            to=receiver
        )

        message.attach_alternative(htmlMessage, "text/html")
        message.send()

    except Exception as e:
        print(e)



#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
from product.models import ProductCategory, IndexProductBanner, IndexPromotionBanner, IndexCategoryProductBanner

@app.task
def generateStaticIndexHtml():

    # To get the product category
    categories = ProductCategory.objects.all()


    # To get the homepage product banner
    productBanners = IndexProductBanner.objects.all().order_by('index')

    # To get the homepage promotion banner
    promotionBanners = IndexPromotionBanner.objects.all().order_by('index')

    # To get the homepage product display information as per category
    for category in categories:
        # If displayCategory is 0, the product category will be shown as title and 1 is image
        titleBanners = IndexCategoryProductBanner.objects.filter(category=category, displayCategory=0).order_by('index')
        imageBanners = IndexCategoryProductBanner.objects.filter(category=category, displayCategory=1).order_by('index')

        category.titleBanners = titleBanners
        category.imageBanners = imageBanners


    # To summarize the response
    context = {'categories': categories,
               'productBanners': productBanners,
               'promotionBanners': promotionBanners}

    temp = loader.get_template('staticIndex.html')
    staticIndexHtml = temp.render(context)

    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')

    with open(save_path, 'w') as f:
        f.write(staticIndexHtml)