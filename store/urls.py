from django.urls import path
from . import views
# from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()  
router.register('product',views.ProductViewSet,basename='product')
router.register('category',views.CategoryViewSet,basename='category')
router.register('cart',views.CartViewSet,basename='cart')


product_router = routers.NestedDefaultRouter(router, 'product', lookup='product')
product_router.register('comments',views.CommentViewSet,basename='product-comments')

urlpatterns = router.urls + product_router.urls

# urlpatterns = [
#     path('product/',views.ProductList.as_view() , name = "product_list"),
#     path('product/<int:pk>',views.ProductDetail.as_view() , name = "product_detail"),
#     path('category/',views.CategoryList.as_view() , name = "category_list"),
#     path('category/<int:pk>',views.CategoryDetail.as_view() , name = "category_detail")
# ]
