from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login as auth_login
from .models import Category, Product
from firstproject.forms import CartAddProductForm, ProductForm, UserRegistrationForm
from rest_framework import generics
from .serializers import ProductSerializer, CategorySerializer

def info_view(request):
    return render(request, 'info.html')

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request,
                  'product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products})

def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm()
    return render(request,
                  'product/detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form})

@login_required
@permission_required('firstproject.add_product', raise_exception=True)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect('firstproject:product_detail', id=product.id, slug=product.slug)
    else:
        form = ProductForm()
    return render(request, 'product/product_form.html', {'form': form, 'operation': 'create'})

@login_required
@permission_required('firstproject.change_product', raise_exception=True)
def product_update(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            return redirect('firstproject:product_detail', id=product.id, slug=product.slug)
    else:
        form = ProductForm(instance=product)
    return render(request, 'product/product_form.html', {'form': form, 'product': product, 'operation': 'update'})

@login_required
@permission_required('firstproject.delete_product', raise_exception=True)
def product_delete(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    if request.method == 'POST':
        product.delete()
        return redirect('firstproject:product_list')
    return render(request, 'product/product_confirm_delete.html', {'product': product})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('firstproject:product_list') # Redirect to home or a success page
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

class ProductListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-created')
    serializer_class = ProductSerializer

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
