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
from django.contrib.auth.decorators import login_required
from .views import (
    RegisterView,
    ActivateView,
    ActivationLinkExpiresView,
    LoginView,
    LogoutView,

    PasswordResetView,
    PasswordResetLinkExpiresView,
    PasswordResetConfirmView,
    PasswordResetSuccessView,
    PasswordResetFailView,
    
    UserInfoView,
    UserOrderView,
    SenderAddressView,
    SenderAddressDeleteView,
    ReceiverAddressView,
    ReceiverAddressDeleteView
)

from product.views import (
    ProductCategoryListView
)

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################

urlpatterns = [
    re_path(r'^register$', RegisterView.as_view(), name='register'),
    re_path(r'^activate/(?P<token>.*)$', ActivateView.as_view(), name='activate'),
    re_path(r'^activationlinkexpires$', ActivationLinkExpiresView.as_view(), name='activationLinkExpires'),
    re_path(r'^login$', LoginView.as_view(), name='login'),
    re_path(r'^logout$', LogoutView.as_view(), name='logout'),

    re_path(r'^passwordreset$', PasswordResetView.as_view(), name='passwordReset'),
    re_path(r'^passwordresetlinkexpires$', PasswordResetLinkExpiresView.as_view(), name='passwordResetLinkExpires'),
    re_path(r'reset/(?P<token>.*)$', PasswordResetConfirmView.as_view(), name='passwordResetConfirm'),
    re_path(r'^passwordresetsuccess$', PasswordResetSuccessView.as_view(), name='passwordResetSuccess'),
    re_path(r'^passwordresetfail$', PasswordResetFailView.as_view(), name='passwordResetFail'),

    re_path(r'^$', UserInfoView.as_view(), name='user'),
    re_path(r'^order/(?P<page>\d+)$', UserOrderView.as_view(), name='order'),

    re_path(r'^senderaddress$', SenderAddressView.as_view(), name='senderAddress'),
    re_path(r'^senderaddress/delete$', SenderAddressDeleteView.as_view(), name='senderAddressDelete'),

    re_path(r'^receiveraddress$', ReceiverAddressView.as_view(), name='receiverAddress'),
    re_path(r'^receiveraddress/delete$', ReceiverAddressDeleteView.as_view(), name='receiverAddressDelete'),

]
