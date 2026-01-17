from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import translation
from django.conf import settings
import stripe
import uuid

from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem, 
    Review, SiteSettings, DiscountCode
)

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_site_settings():
    """Get or create site settings"""
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    return settings_obj


def set_language(request, language):
    """Change language"""
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return redirect(request.META.get('HTTP_REFERER', '/'))


def home(request):
    """Home page"""
    site_settings = get_site_settings()
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'site_settings': site_settings,
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def products_list(request):
    """Products listing page"""
    site_settings = get_site_settings()
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(name_ar__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'site_settings': site_settings,
        'products': products,
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'store/products.html', context)


def product_detail(request, slug):
    """Product detail page"""
    site_settings = get_site_settings()
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.filter(is_approved=True)
    
    context = {
        'site_settings': site_settings,
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, 'Product added to cart')
    return redirect('cart')


@login_required
def cart_view(request):
    """Shopping cart page"""
    site_settings = get_site_settings()
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    # Calculate totals
    subtotal = sum(item.get_total() for item in cart_items)
    tax = subtotal * 0.15
    shipping = 0 if subtotal > 500 else 50
    total = subtotal + tax + shipping
    
    context = {
        'site_settings': site_settings,
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('cart')


@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    
    return redirect('cart')


@login_required
def checkout(request):
    """Checkout page"""
    site_settings = get_site_settings()
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('cart')
    
    # Calculate totals
    subtotal = sum(item.get_total() for item in cart_items)
    tax = subtotal * 0.15
    shipping = 0 if subtotal > 500 else 50
    total = subtotal + tax + shipping
    
    if request.method == 'POST':
        # Create order
        order_number = f'ORD-{uuid.uuid4().hex[:8].upper()}'
        
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            customer_name=request.POST.get('customer_name'),
            customer_email=request.POST.get('customer_email'),
            customer_phone=request.POST.get('customer_phone'),
            shipping_address=request.POST.get('shipping_address'),
            subtotal=subtotal,
            tax_amount=tax,
            shipping_amount=shipping,
            final_amount=total,
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_name_ar=item.product.name_ar,
                quantity=item.quantity,
                unit_price=item.product.discount_price or item.product.price,
                total_price=item.get_total(),
            )
        
        # Clear cart
        cart.items.all().delete()
        
        return redirect('payment', order_id=order.id)
    
    context = {
        'site_settings': site_settings,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def payment(request, order_id):
    """Payment page"""
    site_settings = get_site_settings()
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.final_amount * 100),
                currency='sar',
                metadata={'order_id': order.id},
            )
            order.stripe_payment_intent = intent.id
            order.save()
            
            context = {
                'site_settings': site_settings,
                'order': order,
                'client_secret': intent.client_secret,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            }
            return render(request, 'store/payment.html', context)
        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
    
    context = {
        'site_settings': site_settings,
        'order': order,
    }
    return render(request, 'store/order_review.html', context)


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    site_settings = get_site_settings()
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'site_settings': site_settings,
        'order': order,
    }
    return render(request, 'store/order_confirmation.html', context)


@login_required
def orders_list(request):
    """User's orders list"""
    site_settings = get_site_settings()
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'site_settings': site_settings,
        'orders': orders,
    }
    return render(request, 'store/orders.html', context)


@login_required
def add_review(request, product_id):
    """Add product review"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        
        review, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'comment': comment,
            }
        )
        
        # Update product rating
        reviews = product.reviews.filter(is_approved=True)
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
        product.rating = avg_rating
        product.review_count = reviews.count()
        product.save()
        
        messages.success(request, 'Review submitted successfully')
    
    return redirect('product_detail', slug=product.slug)


# Admin views

def admin_dashboard(request):
    """Admin dashboard"""
    if not request.user.is_staff:
        return redirect('home')
    
    site_settings = get_site_settings()
    
    context = {
        'site_settings': site_settings,
    }
    return render(request, 'admin/dashboard.html', context)


def admin_settings(request):
    """Admin site settings"""
    if not request.user.is_staff:
        return redirect('home')
    
    site_settings = get_site_settings()
    
    if request.method == 'POST':
        site_settings.business_name = request.POST.get('business_name', site_settings.business_name)
        site_settings.business_name_ar = request.POST.get('business_name_ar', site_settings.business_name_ar)
        site_settings.contact_email = request.POST.get('contact_email', site_settings.contact_email)
        site_settings.contact_phone = request.POST.get('contact_phone', site_settings.contact_phone)
        site_settings.whatsapp_number = request.POST.get('whatsapp_number', site_settings.whatsapp_number)
        site_settings.address = request.POST.get('address', site_settings.address)
        site_settings.address_ar = request.POST.get('address_ar', site_settings.address_ar)
        site_settings.about_us = request.POST.get('about_us', site_settings.about_us)
        site_settings.about_us_ar = request.POST.get('about_us_ar', site_settings.about_us_ar)
        site_settings.primary_color = request.POST.get('primary_color', site_settings.primary_color)
        site_settings.secondary_color = request.POST.get('secondary_color', site_settings.secondary_color)
        site_settings.accent_color = request.POST.get('accent_color', site_settings.accent_color)
        
        if 'logo' in request.FILES:
            site_settings.logo = request.FILES['logo']
        
        if 'background_image' in request.FILES:
            site_settings.background_image = request.FILES['background_image']
        
        site_settings.save()
        messages.success(request, 'Settings updated successfully')
        return redirect('admin_settings')
    
    context = {
        'site_settings': site_settings,
    }
    return render(request, 'admin/settings.html', context)


def admin_products(request):
    """Admin products management"""
    if not request.user.is_staff:
        return redirect('home')
    
    site_settings = get_site_settings()
    products = Product.objects.all()
    
    context = {
        'site_settings': site_settings,
        'products': products,
    }
    return render(request, 'admin/products.html', context)


def admin_orders(request):
    """Admin orders management"""
    if not request.user.is_staff:
        return redirect('home')
    
    site_settings = get_site_settings()
    orders = Order.objects.all()
    
    context = {
        'site_settings': site_settings,
        'orders': orders,
    }
    return render(request, 'admin/orders.html', context)
