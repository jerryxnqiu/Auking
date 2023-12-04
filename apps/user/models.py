from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from db.baseModel import BaseModel


# Create your models here.
class User(AbstractUser, BaseModel):
    """User Model, inherit from Django user model"""

    class Meta:
        db_table = 'dbUser'
        verbose_name = '01用户表'
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    """Address Manager Model"""

    def getDefaultAddress(self, user):
        """To get the default receiver address"""
        try:
            address = self.get(user=user, isDefault=True)
        except self.model.DoesNotExist:
            address = None

        return address


class SenderAddress(BaseModel):
    """Sender Address Model, depending on 'User' table"""
    
    user = models.ForeignKey('User', verbose_name='账户用户名称', on_delete=models.CASCADE)
    sender = models.CharField(max_length=20, verbose_name='寄件人')
    senderAddr = models.CharField(max_length=256, blank=True, verbose_name='寄件人地址')
    senderTel = models.CharField(max_length=11, verbose_name='寄件人电话')
    isDefault = models.BooleanField(default=False, verbose_name='是否默认')

    # To re-define the new class method
    objects = AddressManager()

    class Meta:
        db_table = 'dbSenderAddress'
        verbose_name = '02发件人信息表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sender


class ReceiverAddress(BaseModel):
    """Receiver Address Model, depending on 'User' table"""
    
    user = models.ForeignKey('User', verbose_name='账户用户名称', on_delete=models.CASCADE)
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    receiverAddr = models.CharField(max_length=256, verbose_name='收件地址')
    receiverTel = models.CharField(max_length=11, verbose_name='收件人电话')
    receiverIdImageFront = models.ImageField(upload_to='images/receiverIdImages', max_length=255, verbose_name='收件人身份证正面图片路径')
    receiverIdImageBack = models.ImageField(upload_to='images/receiverIdImages', max_length=255, verbose_name='收件人身份证背面图片路径')
    isDefault = models.BooleanField(default=False, verbose_name='是否默认')

    # To re-define the new class method
    objects = AddressManager()

    class Meta:
        db_table = 'dbReceiverAddress'
        verbose_name = '03收件人信息表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.receiver
