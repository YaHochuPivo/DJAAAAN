from django.urls import path
from . import views

app_name = 'firstproject'

urlpatterns = [
    path('info', views.info_view, name='info_view'),
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('register/', views.register, name='register'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('<int:id>/<slug:slug>/update/', views.product_update, name='product_update'),
    path('<int:id>/<slug:slug>/delete/', views.product_delete, name='product_delete'),
    path('api/products/', views.ProductListAPIView.as_view(), name='api_product_list'),
    path('api/products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('api/categories/', views.CategoryListAPIView.as_view(), name='api_category_list'),
]
