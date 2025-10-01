from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True)
    top_product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, blank=True, null=True, related_name="+"
    )

    def __str__(self):
        return self.title


class Discount(models.Model):
    discount = models.FloatField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{str(self.discount)} | {self.description}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    slug = models.SlugField()
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    discounts = models.ManyToManyField(Discount, blank=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer"
    )
    # mitonim  b  do  ravesh  bala  v  apiin  braye ezafe  krdn  user  asli site  b  karbaran  estefade  konim
    # haji hoseini gofte  k  ravesh  bala ii bhine tare chon yek  string  brmigrade
    # vli   dar  paiini  zamani k  ma  b  khoroji ham niazi  ndashte  bashim
    # bazm miad  table  user ro  bramon ama de  mikone  v in  dar  pas  zamine  etefaq  khobi  nis
    # *****
    # user = models.OneToOneField(
    #     get_user_model, on_delete=models.CASCADE, related_name="customer"
    # )
    # *****
    phone_number = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Address(models.Model):
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, primary_key=True
    )
    province = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)


class UnpaidOrderManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.ORDER_STATUS_UNPAID)


class Order(models.Model):
    ORDER_STATUS_PAID = "p"
    ORDER_STATUS_UNPAID = "u"
    ORDER_STATUS_CANCELED = "c"
    ORDER_STATUS = [
        (ORDER_STATUS_PAID, "Paid"),
        (ORDER_STATUS_UNPAID, "Unpaid"),
        (ORDER_STATUS_CANCELED, "Canceled"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="orders"
    )
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=1, choices=ORDER_STATUS, default=ORDER_STATUS_UNPAID
    )

    objects = models.Manager()
    unpaid_orders = UnpaidOrderManger()

    def __str__(self):
        return f"Order id={self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = [["order", "product"]]


class CommentManger(models.Manager):
    def get_approved(self):
        return self.get_queryset().filter(status=Comment.COMMENT_STATUS_APPROVED)


class ApprovedCommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Comment.COMMENT_STATUS_APPROVED)


class Comment(models.Model):
    COMMENT_STATUS_WAITING = "w"
    COMMENT_STATUS_APPROVED = "a"
    COMMENT_STATUS_NOT_APPROVED = "na"
    COMMENT_STATUS = [
        (COMMENT_STATUS_WAITING, "Waiting"),
        (COMMENT_STATUS_APPROVED, "Approved"),
        (COMMENT_STATUS_NOT_APPROVED, "Not Approved"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="comments"
    )
    name = models.CharField(max_length=255)
    body = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=2, choices=COMMENT_STATUS, default=COMMENT_STATUS_WAITING
    )

    objects = CommentManger()
    approved = ApprovedCommentManager()


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [["cart", "product"]]
