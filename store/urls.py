from django.urls import path
from . import views

urlpatterns = [
    # Frontend URLs
    path('', views.home, name='home'),
    path('products/', views.products_list, name='products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    
    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.orders_list, name='orders'),
    
    # Review URLs
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    
    # Language URLs
    path('set-language/<str:language>/', views.set_language, name='set_language'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
]
