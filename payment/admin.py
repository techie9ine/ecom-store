from django.contrib import admin

from .models import ShippingAddress, Order
from .models import ShippingAddress, OrderItem
# Register your models here.

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)
