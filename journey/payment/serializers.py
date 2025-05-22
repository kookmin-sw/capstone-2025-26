from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'aid', 'tid', 'cid', 'sid',
            'partner_order_id', 'partner_user_id', 'payment_method_type',
            'item_name', 'quantity', 'total', 'tax_free', 'vat',
            'point', 'discount', 'green_deposit', 'status',
            'created_at', 'approved_at'
        ]
        read_only_fields = ['id']
