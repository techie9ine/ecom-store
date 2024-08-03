from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib import messages

from .models import Category, Product
from .forms import UserRegisterForm, UserLoginForm, ProductRegisterForm

from payment.models import ShippingAddress
from payment.forms import ShippingForm


def home(request):
    products = Product.objects.all()

    context = {"products": products}
    return render(request, "coreApp/home.html", context)


def signup(request):
    form = UserRegisterForm()

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("coreApp:login")

    context = {"form": form}
    return render(request, "coreApp/signup.html", context)


def login_view(request):
    form = UserLoginForm()

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("coreApp:home")

    context = {
        "form": form,
    }
    return render(request, "coreApp/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("coreApp:login")


def category(request):
    all_categories = Category.objects.all()
    return {"all_categories": all_categories}


@login_required
def new_item(request):
    form = ProductRegisterForm()

    if request.method == "POST":
        form = ProductRegisterForm(request.POST, request.FILES)  # Because we are adding images from the frontend

        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()

            return redirect("coreApp:home")

    context = {
        "form": form,
        "title": "Add New Item",
    }
    return render(request, "coreApp/new_item.html", context)


def detail(request, pk):
    # product = Product.objects.get(pk=pk)
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)

    context = {
        "product": product,
        "related_products": related_products,
    }
    return render(request, "coreApp/item_detail.html", context)


@login_required
def update_item(request, pk):
    # product = Product.objects.get(pk=pk, created_by=request.user)
    product = get_object_or_404(Product, pk=pk, created_by=request.user)

    form = ProductRegisterForm(instance=product)

    if request.method == "POST":
        form = ProductRegisterForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("coreApp:home")

    context = {
        "title": "Edit Product",
        "form": form,
    }
    return render(request, "coreApp/new_item.html", context)


@login_required
def delete(request, pk):
    product = get_object_or_404(Product, pk=pk, created_by=request.user)

    if request.method == "POST":
        product.delete()
        return redirect("coreApp:home")

    context = {"product": product}
    return render(request, "coreApp/delete.html", context)


def search(request):
    query = request.GET.get("query", "")
    products = Product.objects.filter(is_sold=False)

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    context = {
        "query": query,
        "products": products
    }
    return render(request, "coreApp/search.html", context)

@login_required
def dashboard(request):
    products = Product.objects.filter(created_by=request.user)

    context = {
        "products": products
    }
    return render(request, "coreApp/dashboard.html", context)


@login_required
def manage_shipping(request):
    try:
        # Account user with shipment information
        shipping = ShippingAddress.objects.get(user=request.user.id)
    except ShippingAddress.DoesNotExist:
        # Account user with no shipment information
        shipping = None

    form = ShippingForm(instance=shipping)
    if request.method == 'POST':
        form = ShippingForm(request.POST, instance=shipping)
        if form.is_valid():
            # Assign the user FK on the object
            shipping_user = form.save(commit=False)
            # Adding the FK itself
            shipping_user.user = request.user

            shipping_user.save()
            messages.info(request, "Update success!")
            return redirect('coreApp:home')
    context = {'form': form}
    return render(request, 'coreApp/manage_shipping.html', context)




