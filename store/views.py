# from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

# from rest_framework.views import APIView
# from rest_framework.generics import ListCreateAPIView ,RetrieveUpdateDestroyAPIView
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Cart, Category, Comment, Product
from .paginations import TenPerPagePagination
from .serializers import (
    CartSerializer,
    CategorySerializer,
    CommentSerializer,
    ProductSerializer,
)

# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related('category').all()
#         serializer = ProductSerializer(queryset,many=True,context={'request': request})
#         return Response(serializer.data)
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data , status=201)


# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.select_related('category').all()
#     serializer_class = ProductSerializer
#     def get_serializer_context(self):
#         return {'request': self.request}

# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     serializer_class = ProductSerializer
#     queryset = Product.objects.select_related('category').all()

#     def delete(self, request, pk):
#         product = get_object_or_404(Product,pk=pk)
#         if product.order_items.count() > 0:
#             return Response('cant delete',status=405)
#         product.delete()
#         return Response('deleted',status=204)


class ProductViewSet(ModelViewSet):
    # queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    queryset = Product.objects.select_related("category").all()
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["unit_price", "name"]
    search_fields = ["name", "category__title"]
    filterset_fields = ["category_id", "inventory"]
    pagination_class = TenPerPagePagination
    # ag  bkhaim  filter  b  sorat  customize shode  dashte  bashim  mitonim  in kar ro  anjam  bedim
    # biaim  to hmin app  yek  file  jadid  be  name  filters.py  besazim  va  toosh  yek  class  besazim  k az  django_filters.FilterSet  ers  bbare
    # v baad  to  in class  mitonim  filter  haye  customize shode  ro tarif konim  va  to inja  importesh konim  va  be jaye  DjangoFilterBackend

    #    ******==>> filterset_class = ProductFilter ==>> IMPORT KRDNE  ON AZ  filters.py YADMON  NARE

    # in ravesh  zir  b sorat  sonaty  b  qadimi bod  k khodm braye  filter sazi  anjam midadm  ama  ba esterade  az  package  django  filter  mitonim in kar
    # ro  b sorat kholase  tr  b  shekle  bala  tnha  dar  3 khat  code  anjam  bedim
    # def get_queryset(self):
    #     base_queryset  = Product.objects.select_related('category').all()
    #     category_id = self.request.query_param.get('category_id')
    #     if category_id is not None :
    #         return Product.objects.select_related('category').filter(category_id=category_id)
    #     return base_queryset

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.order_items.count() > 0:
            return Response("cant delete", status=405)
        product.delete()
        return Response("deleted", status=204)


# class CategoryList(APIView):
#     def get(self, request):
#         queryset = Category.objects.prefetch_related('products').all()
#         serializer = CategorySerializer(queryset,many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = CategorySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data , status=201)
# class CategoryList(ListCreateAPIView):
#     queryset = Category.objects.prefetch_related('products').all()
#     serializer_class = CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.prefetch_related("products").all()
    serializer_class = CategorySerializer

    def destroy(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        if category.products.count() > 0:
            return Response("cant delete becasue cat  has  some  products", status=405)
        category.delete()
        return Response("deleted", status=204)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        # product_pk = self.kwargs['product_pk']
        return Comment.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_pk": self.kwargs.get("product_pk")}


class CartViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
