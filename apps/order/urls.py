"""
URL configuration for auking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path, include
from .views import (
    OrderPlaceView,
    OrderCommitView,

    OrderDetailsView,

    CreateCheckoutSessionView,
    CheckoutSuccessView,
    CheckoutCancelView,

    stripeWebhook,
    weChatPayWebhook,
    aliPayWebhook,

    BankTransferDetailsView,
)

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################

urlpatterns = [
    re_path(r'^orderplace$', OrderPlaceView.as_view(), name='orderPlace'),
    re_path(r'^commit$', OrderCommitView.as_view(), name='commit'),

    re_path(r'^details/(?P<orderId>\d+)$', OrderDetailsView.as_view(), name='orderDetails'),
    
    re_path(r'^createcheckoutsession/(?P<orderId>\d+)$', CreateCheckoutSessionView.as_view(), name='createCheckoutSession'),
    re_path(r'^checkoutsuccess$', CheckoutSuccessView.as_view(), name='checkoutSuccess'),
    re_path(r'^checkoutcancel$', CheckoutCancelView.as_view(), name='checkoutCancel'),

    re_path(r'^stripewebhook', stripeWebhook, name='stripWebhook'),
    re_path(r'^wechatpaywebhook', weChatPayWebhook, name='weChatPayWebhook'),
    re_path(r'^alipaywebhook', aliPayWebhook, name='aliPayWebhook'),

    re_path(r'^banktransferdetails$', BankTransferDetailsView.as_view(), name='bankTransferDetailsView'),

]
