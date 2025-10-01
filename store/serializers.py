from decimal import Decimal

from django.utils.text import slugify
from rest_framework import serializers

from .models import Cart, CartItem, Category, Comment, Product

DOLLORS_IN_RIAL = 95000


class CategorySerializer(serializers.ModelSerializer):
    count_of_products_for_category = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "title",
            "description",
            "count_of_products_for_category",
        ]

    # def create(self, validated_data):
    #     return Category.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.description = validated_data.get('description', instance.description)
    #     instance.save()
    #     return instance

    def get_count_of_products_for_category(self, category: Category):
        return category.products.count()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "unit_price",
            "unit_price_after_tax",
            "inventory",
            "price_rial",
            "category",
            "category_link",
        ]

    # id = serializers.IntegerField()
    ### title = serializers.CharField(max_length=255 , source='name')
    # name = serializers.CharField(max_length=255 )
    # unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    unit_price_after_tax = serializers.SerializerMethodField()
    # inventory = serializers.IntegerField()
    price_rial = serializers.SerializerMethodField(method_name="calculate_price_rial")
    # category = serializers.StringRelatedField()
    category = CategorySerializer()
    category_link = serializers.HyperlinkedRelatedField(
        queryset=Category.objects.all(),
        view_name="category-detail",
        source="category",
    )

    def calculate_price_rial(self, product):
        return int(product.unit_price * DOLLORS_IN_RIAL)

    # def get_price_rial(self,product):
    #     return int(product.unit_price * DOLLORS_IN_RIAL)

    def get_unit_price_after_tax(self, product):
        return round(product.unit_price * Decimal(1.09), 2)

    # create  custom  validation  for fields
    def validate(self, data):
        if len(data["name"]) < 6:
            raise serializers.ValidationError(
                "name  length  must  be  more  than  6  char"
            )
        return data

    # over ride  create  method  for  post  request
    def create(self, validated_data):
        product = Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product

    def update(self, instance, validated_data):
        instance.inventory = validated_data.get("inventory", instance.inventory)
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "name",
            "body",
        ]

    def create(self, validated_data):
        return Comment.objects.create(
            product_id=self.context.get("product_pk"), **validated_data
        )


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "unit_price"]


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity"]

    def create(self, validated_data):
        cart_id = self.context.get("cart_pk")
        product = validated_data.get("product")
        quantity = validated_data.get("quantity")
        try:
            cart_item = (
                CartItem.objects.select_related("cart")
                .select_related("product")
                .get(cart_id=cart_id, product_id=product.id)
            )
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **validated_data)

        return cart_item


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]
        read_only_fields = ["id"]

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    # def create(self, validated_data):
    #     cart_id = self.context.get('cart_id')
    #     return CartItem.objects.create(cart_id=cart_id, **validated_data)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "cart_total_price"]
        read_only_fields = ["id"]

    def get_cart_total_price(self, cart: Cart):
        return sum(
            [item.quantity * item.product.unit_price for item in cart.items.all()]
        )
        # return sum([item.total_price for item in cart.items.all()])


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]
