from django.db import models
from db.baseModel import BaseModel
from tinymce.models import HTMLField


# Create your models here.
class OrderInfo(BaseModel):
    """Order Model, one line per order, depending on 'User' table"""

    PAYMENT_METHODS = {
        1: '微信',
        2: '支付宝',
        3: 'VISA/Master',
        4: '银行转账'
    }

    PAYMENT_METHODS_ENUM = {
        "WechatPAY": 1,
        "AliPAY": 2,
        "VISA/Master": 3,
        "Bank Transfer": 4
    }

    PAYMENT_METHOD_CHOICES = (
        (1, '微信'),
        (2, '支付宝'),
        (3, 'VISA/Master'),
        (4, '银行转账'),
    )

    ORDER_STATUS_ENUM = {
        "Unpaid": 1,
        "Paid, to be sent": 2,
        "Sent, to be received": 3,
        "Received, to be commented": 4,
        "All completed": 5
    }

    ORDER_STATUS = {
        1: '待支付',
        2: '已支付，待发货',
        3: '已发货，待收货',
        4: '已收货，待评价',
        5: '全已完成'
    }

    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '已支付，待发货'),
        (3, '已发货，待收货'),
        (4, '已收货，待评价'),
        (5, '全已完成')
    )

    orderId = models.CharField(max_length=128, primary_key=True, verbose_name='订单号')

    user = models.ForeignKey('user.user', verbose_name='用户', on_delete=models.CASCADE)
    
    sender = models.CharField(max_length=20, verbose_name='寄件人')
    senderAddr = models.CharField(max_length=256, blank=True, verbose_name='寄件人地址')
    senderTel = models.CharField(max_length=11, verbose_name='寄件人电话')

    receiverAddressId = models.IntegerField(default=1, verbose_name='收件人信息ID')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    receiverAddr = models.CharField(max_length=256, verbose_name='收件地址')
    receiverTel = models.CharField(max_length=11, verbose_name='收件人电话')

    logisticsCompanyName = models.CharField(max_length=32, verbose_name='物流公司名称')
    logisticsParcelCount = models.IntegerField(default=1, verbose_name='物流包裹数量')
    
    paymentMethod = models.SmallIntegerField(choices=PAYMENT_METHOD_CHOICES, default=1, verbose_name='支付方式')

    totalSkuQty = models.IntegerField(default=1, verbose_name='商品数量')
    totalSkuPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')

    totalServiceQty = models.IntegerField(default=1, verbose_name='服务数量')
    totalServicePrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='服务总价')

    totalLogisticsWeight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='物流总重量')
    logisticsUnit = models.CharField(max_length=10, verbose_name='物流单位')
    totalLogisticsPrice = models.DecimalField(max_digits=10, decimal_places=2,verbose_name='物流总价')

    totalHandlingFee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='交易手续费')
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单总价')
    orderStatus = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')

    orderNotes = models.CharField(max_length=1024, default='', verbose_name='订单备注')

    # Alipay, Wechat Pay, Union Pay receipt number if there is
    # Stripe:   charge ID
    # 
    tradeNo = models.CharField(max_length=128, default='', verbose_name='支付编号')
    
    # Stripe:   payment intend
    paymentIntentDescription = models.CharField(max_length=128, default='', verbose_name='支付描述')
    paymentInvoicePdfUrl = models.FileField(upload_to="paymentInvoicePdf/", default='', max_length=255, verbose_name='Stripe的支付发票')

    class Meta:
        db_table = 'dbOrderInfo'
        verbose_name = '01订单表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.orderId


class OrderProduct(BaseModel):
    """Order Product Model, one product per line, unique product item in each order, 
    to capture the products inside a order, depending on 'orderInfo' table"""

    order = models.ForeignKey('orderInfo', verbose_name='订单', on_delete=models.CASCADE)

    skuId = models.CharField(max_length=128, verbose_name='商品ID')
    skuName = models.CharField(max_length=192, verbose_name='商品SKU名称')
    skuCount = models.IntegerField(default=1, verbose_name='商品SKU数量')
    skuUnit = models.CharField(max_length=20, verbose_name='商品计价单位')
    skuPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    skuGst = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='消费税GST')
    comment = models.CharField(max_length=256, default='', verbose_name='评论')

    class Meta:
        db_table = 'dbOrderProduct'
        verbose_name = '02订单商品表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.skuName


class OrderProductandServiceMapping(BaseModel):
    """Order Service Model, one service per line, unique service item for a product (skuIndex) in a parcelId,
    to capture the service content for each product inside each parcel, depending on 'orderInfo' table"""

    order = models.ForeignKey('orderInfo', verbose_name='订单', on_delete=models.CASCADE)

    parcelId = models.IntegerField(default=1, verbose_name='包裹序号')

    skuIndex = models.CharField(max_length=128, verbose_name='订单内商品唯一编号')
    skuId = models.CharField(max_length=128, verbose_name='包裹内商品ID')
    skuName = models.CharField(max_length=192, verbose_name='包裹内商品名称')

    serviceName = models.CharField(max_length=32, verbose_name='服务名称')
    serviceImage = models.ImageField(upload_to='images/services', max_length=255, verbose_name='服务交付图片')
    serviceUnit = models.CharField(max_length=10, verbose_name='服务单位')
    servicePrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='服务价格(含GST)小计')
    serviceGst = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='服务价格消费税GST小计')

    class Meta:
        db_table = 'dbOrderService'
        verbose_name = '03订单箱子商品与服务匹配表'
        verbose_name_plural = verbose_name    

    def __str__(self):
        return self.serviceName


class OrderTracking(BaseModel):
    """Order Tracking Model, one parcel per line, unique parcel item in each order,
    to capture what they are inside each parcel and tag tracking Id with it, depending on 'orderInfo' table"""

    order = models.ForeignKey('orderInfo', verbose_name='订单', on_delete=models.CASCADE)

    logisticsCompanyName = models.CharField(max_length=32, verbose_name='物流公司名称')
    parcelId = models.IntegerField(default=1, verbose_name='包裹序号')
    skuQty = models.IntegerField(default=1, verbose_name='包裹内商品数量')
    parcelWeight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='包裹重量')
    parcelPostage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='包裹物流价钱')
    trackingId = models.CharField(max_length=128, verbose_name='物流单号')
    trackingImage = models.ImageField(upload_to='images/logistics', max_length=255, verbose_name='物流面单')

    class Meta:
        db_table = 'dbOrderTracking'
        verbose_name = '04订单物流跟踪'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.trackingId

