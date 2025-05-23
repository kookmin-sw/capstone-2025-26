from django.db import models

class Payment(models.Model):
    """결제 모델"""
    STATUS_CHOICES = [
        ('ready', '결제 준비'),
        ('approved', '결제 승인'),
        ('failed', '결제 실패'),
        ('canceled', '결제 취소'),
    ]

    user = models.ForeignKey('user_manager.User', on_delete=models.CASCADE, related_name='payments')
    aid = models.CharField(max_length=50, null=True, blank=True)  # 승인번호
    tid = models.CharField(max_length=50)  # 결제 고유번호
    cid = models.CharField(max_length=50)  # 가맹점 코드
    sid = models.CharField(max_length=50, null=True, blank=True)  # 정기결제 ID
    partner_order_id = models.CharField(max_length=50)  # 가맹점 주문번호
    partner_user_id = models.CharField(max_length=50)  # 가맹점 회원 ID
    payment_method_type = models.CharField(max_length=50, null=True, blank=True)  # 결제 수단
    item_name = models.CharField(max_length=100)  # 상품명
    quantity = models.IntegerField()  # 상품 수량
    total = models.IntegerField()  # 결제 금액
    tax_free = models.IntegerField()  # 비과세 금액
    vat = models.IntegerField()  # 부가세 금액
    point = models.IntegerField(default=0)  # 사용한 포인트
    discount = models.IntegerField(default=0)  # 할인 금액
    green_deposit = models.IntegerField(default=0)  # 컵 보증금
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)  # 결제 상태
    created_at = models.DateTimeField()  # 결제 준비 시간
    approved_at = models.DateTimeField(null=True, blank=True)  # 결제 승인 시간

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.item_name} ({self.status})"

