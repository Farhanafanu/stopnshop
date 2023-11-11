from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import cache_control, never_cache
from django.contrib import messages
from .models import Customer, Product, Category,Sub_category,Variation
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from django.db.models import Count
from datetime import datetime
import io
import base64
import matplotlib.pyplot as plt
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from email.message import EmailMessage
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import io
import uuid
import json
import string
import random
import smtplib
from . import manager
from django.http import JsonResponse
from .models import Wishlist,Cart,OrderItem,Order
from django.db.models import Q
from .models import Customer 
from .models import *
import random
import string
import secrets
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.core.mail import send_mail
import razorpay
from django.conf import settings
from razorpay import Client
from .models import *
from ban.models import Banner
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import traceback

# Import your custom Customer model


# Create your views here.
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def base(request):
    if 'email' in request.session:
        return redirect('home')
    return render(request, 'base.html')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def home(request):
    banner = Banner.objects.all()
    if 'email' in request.session:
        return redirect('home')
    elif 'admin' in request.session:
        return redirect('dashboard')
    else:
        section = Section.objects.filter(name='Top deal of the day').first()
        product = Product.objects.filter(section__name='Top deal of the day')
        context = {
            'section': section,
            'product': product,
             'banner': banner,
        }
        return render(request, 'Main/home.html', context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def loginhome(request):
    if 'email' in request.session:
        return redirect('home')
    if request.method == "POST":
        email = request.POST.get('email')  # Use 'email' instead of 'username'
        password = request.POST.get('password')
        if Customer.objects.filter(email=email).exists():
            check=Customer.objects.get(email=email)
            if not check.is_superuser:
                user = authenticate(request, email=email, password=password)
                print(email,password)
                print(user)
                if user is not None:
                    login(request, user)  
                    return redirect('home')
                else:
                    messages.error(request, 'Email and password are invalid!')
                    return redirect('handlelogin')
            else:
                messages.error(request, 'Sorry!You cant Login Here.')        
        else:
            messages.error(request, 'This email doesnt has any linked account.')        
        # Authenticate against your custom Customer model using email   
    return render(request,'registration/login.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def register(request):
    if 'email' in request.session:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('handleregister')
        message = generate_otp()
        sender_email = "stopnshop890@gmail.com"
        receiver_mail = email
        password_email = "qoruttdlboezrrcc"
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password_email)
                server.sendmail(sender_email, receiver_mail, message)
        except smtplib.SMTPAuthenticationError:
            messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
            return redirect('handleregister')
        user = Customer.objects.create_user(username=username, password=password, email=email)
        user.save()
        request.session['email'] =  email
        request.session['otp']   =  message
        messages.success (request, 'OTP is sent to your email')
        print("..............reac")
        return redirect('verify_signup')
    return render(request,'registration/loginreg.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def verify_signup(request):
    context = {
        'messages': messages.get_messages(request)
    }
    if request.method == "POST":  
        user      =  Customer.objects.get(email=request.session['email'])
        x         =  request.session.get('otp')
        OTP       =  request.POST['otp']
        if OTP == x:
            user.is_verified = True
            user.save()
            del request.session['email'] 
            del request.session['otp']
            auth.login(request,user)
            messages.success(request, "Signup successful!")
            return redirect('handlelogin')
        else:
            user.delete()
            messages.info(request,"invalid otp")
            del request.session['email']
            return redirect('signup')
    return render(request,'verifiedotp.html',context)
          
# Send the OTP via email
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            customer = Customer.objects.get(email=email)
            if customer.email == email:
                message = generate_otp()
                sender_email = "stopnshop890@gmail.com"
                receiver_mail = email
                password = "qoruttdlboezrrcc"
                try:
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_mail, message)
                except smtplib.SMTPAuthenticationError:
                    messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
                    return redirect('handleregister')
                request.session['email'] =  email
                request.session['otp']   =  message
                messages.success (request, 'OTP is sent to your email')
                return redirect('reset_password')     
        except Customer.DoesNotExist:
            messages.info(request,"Email is not valid")
            return redirect('handlelogin')
    else:
        return redirect('handlelogin')

def generate_otp(length = 6):
    return ''.join(secrets.choice("0123456789") for i in range(length)) 

def reset_password(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        stored_otp = request.session.get('otp')
        if entered_otp == stored_otp:
            if new_password == confirm_password:
                email = request.session.get('email')
                try:
                    customer = Customer.objects.get(email=email)
                    customer.set_password(new_password)
                    customer.save()
                    del request.session['email'] 
                    del request.session['otp']
                    messages.success(request, 'Password reset successful. Please login with your new password.')
                    return redirect('handlelogin')
                except Customer.DoesNotExist:
                    messages.error(request, 'Failed to reset password. Please try again later.')
                    return redirect('handlelogin')
            else:
                messages.error(request, 'New password and confirm password do not match.')
                return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please enter the correct OTP.')
            return redirect('reset_password')
    else:
        return render(request, 'passwordreset.html')
 
#Adminlogin
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def admin_login(request):
    if 'email' in request.session:
        return redirect('home')
    elif 'admin' in request.session:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            email      =  request.POST.get('email')
            pass1      =  request.POST.get('pass')
            user       =  authenticate(request,email=email,password = pass1)
            print(user)
            if user is not None and user.is_superuser:
                login(request,user)
                request.session['admin']=email
                return redirect('dashboard')
            else:
                messages.error(request,"username or password is not same")
                return render(request, 'admin_login.html') 
        else:
             return render (request,'admin_login.html')

# Create bar chart function
def create_bar_chart(labels, data, title):
    plt.figure(figsize=(8, 6))
    plt.bar(labels, data, color='skyblue')
    plt.xlabel('Products')
    plt.ylabel('Amount')
    plt.title(title)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return f'data:image/png;base64,{chart_image}'

# Create pie chart function
def create_pie_chart(labels, data, title):
    plt.figure(figsize=(8, 8))
    plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return f'data:image/png;base64,{chart_image}'
# Import necessary modules
import json
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def dashboard(request):
    products = Product.objects.order_by('-id')
    # Process product data for bar chart (order distribution)
    order_labels = [f'Order {product.id}' for product in products]
    order_amounts = [product.price for product in products]  # Use any field you want for the order amount
    # Process product data for pie chart (stock distribution)
    stock_labels = [product.product_name for product in products]
    stock_amounts = [product.stock for product in products]
    # Convert data to JSON format for JavaScript
    order_data = json.dumps(order_amounts)
    stock_data = json.dumps(stock_amounts) 
    context = {
        'order_labels': order_labels,
        'order_data': order_data,
        'stock_labels': stock_labels,
        'stock_data': stock_data,
    }
    if 'admin' in request.session:
        return render(request, 'dashboard.html', context)
    else:
        return redirect('admin')
@never_cache   
def admin_logout(request):
    if 'admin' in request.session:
        request.session.flush()
    logout(request)
    return redirect('admin')
#customers
@never_cache 
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def customers(request):
    if 'admin' in request.session:    
        customer_list =  Customer.objects.filter(is_staff=False).order_by('id')
        paginator = Paginator(customer_list,10)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'customer.html', context)
    else:
        return redirect('admin')
    
def unblock_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except ObjectDoesNotExist:
        return redirect('customer')  
    customer.is_active = not customer.is_active
    customer.save()
    return redirect('customer')

def block_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return redirect('customer')  
    customer.is_active = False
    customer.save()
    return redirect('customer')     

def shop(request):
    # Get all products and unique colors
    all_products = Product.objects.all()
    unique_colors = all_products.values('color').annotate(count=Count('color')).order_by('color')
    # Get unique categories
    categories = Category.objects.values('category_name').distinct()
    # Get filter parameters from the request
    selected_color = request.GET.get('color')
    selected_price = request.GET.get('price')
    selected_category = request.GET.get('category')
    # Start with all products and filter based on selected options
    products = all_products
    if selected_color:
        products = products.filter(color=selected_color)
    if selected_category:
         products = products.filter(category__category_name=selected_category)
    if selected_price:
        # Define price ranges based on selected_price
        price_ranges = {
            "price1": (0, 500),
            "price2": (500, 1000),
            "price3": (1000, 1500),
            "price4": (1500, 2000),
            "price5": (2000, 2500),
            "price6": (2500, 3000),
            "price7": (3001, 1000000)  
        }
        if selected_price in price_ranges:
            price_range = price_ranges[selected_price]
            # Filter for products with prices within the selected price range
            products = products.filter(price__range=price_range)
    # Now, after all filtering, add discounted_price and offer_price attributes
    for product in products:
        discounted_price = None
        if product.category.category_offer:
    # Calculate the discount amount as a percentage of the original price
            discount_amount = (product.price * product.category.category_offer) / 100
    # Subtract the discount amount from the original price to get the discounted price
            discounted_price = product.price - discount_amount
            product.discounted_price = discounted_price
            offer_price = None
        if product.product_offer:
            offer_price = product.price - (product.price * product.product_offer/100)
        product.offer_price = offer_price
    context = {
        'all_products': all_products,
        'products': products,
        'unique_colors': unique_colors,
        'categories': categories,
    }
    return render(request, 'shop.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache    
def userproductpage(request, id): 
    product = Product.objects.filter(id=id).first()
    discounted_price = None
    offer_price = None
    if product.category.category_offer:
    # Calculate the discount amount as a percentage of the original price
            discount_amount = (product.price * product.category.category_offer) / 100
    # Subtract the discount amount from the original price to get the discounted price
            discounted_price = product.price - discount_amount
            product.discounted_price = discounted_price
            offer_price = None
    if product.product_offer:
        offer_price        = product.price -(product.price * product.product_offer/100)
    product.offer_price    = offer_price
    context = {
        'product': product,
        'discounted_price': discounted_price,
        
    } 
    return render(request, 'userproduct.html', context)
#profile
@user_passes_test(lambda u: not u.is_staff, login_url='login')
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def profile(request):
    user=request.user
    context={
        'user':user,
    }
    return render(request,'profile.html',context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_profile(request):
    if request.method=='POST':
        user=request.user
    # retrive  data  from form
        username = request.POST.get('username')
        new_mail = request.POST.get('email')
        print(username)
    # update the users info
        user.username=username
        user.email=new_mail
        print(user)
        user.save()
        messages.success(request,'Profile updated successfully!!!')
        return redirect('profile')
    return render(request,'profile.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def changepassword(request):
    if request.method == 'POST':
        old_password = request.POST.get('old')
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')
        customer = Customer.objects.get(username=request.user.username)
        if customer.check_password(old_password):
            if new_password == confirm_password:
                customer.set_password(new_password)
                customer.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('home')
            else:
                messages.error(request, 'New password and confirm password do not match.')
                return redirect ('profile')
        else:
            messages.error(request, 'Old password is incorrect.')
            return redirect('profile')
    return render(request, 'profile.html')
#address
def address(request):
    user = request.user
    address = Address.objects.filter(user=user)
    context={
        'address':address,
    }
    return render(request,'address.html',context)

def add_address(request):
    if request.method == 'POST':
        # Retrieve data from the POST request
        full_name = request.POST['full_name']
        house_no = request.POST['house_no']
        post_code = request.POST['post_code']
        state = request.POST['state']
        street = request.POST['street']
        phone_no = request.POST['phone_no']
        city = request.POST['city']
        is_default = request.POST.get('is_default') 
        # Create a new Address object and save it to the database
        user=request.user
        address = Address(
            user=user,
            full_name=full_name,
            house_no=house_no,
            post_code=post_code,
            state=state,
            street=street,
            phone_no=phone_no,
            city=city,
            is_default=is_default == 'on'
        )
        address.save()
        if address.is_default:
            Address.objects.exclude(id=address.id).update(is_default=False)
        return redirect('address') # Redirect to the address list page or any other page
    return render(request,'add_address.html') 
    
def edit_address(request,id):
    address= Address.objects.get(id=id)
    if request.method == 'POST':
        # Retrieve data from the POST request
        full_name = request.POST['full_name']
        house_no = request.POST['house_no']
        post_code = request.POST['post_code']
        state = request.POST['state']
        street = request.POST['street']
        phone_no = request.POST['phone_no']
        city = request.POST['city']
        # Update the Address object with the edited data
        address.full_name = full_name
        address.house_no = house_no
        address.post_code = post_code
        address.state = state
        address.street = street
        address.phone_no = phone_no
        address.city = city
        # Save the updated address to the database
        address.save()
        return redirect('address')
    else:
        context = {
            'address': address
        }
    return render(request,'edit_address.html',context)

def delete_address(request,id):
    try:
        address = Address.objects.get(id=id)
    except Address.DoesNotExist:
        return render(request, 'Address_not_found.html')
    address.delete()
    return redirect('address')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache   
def userlogout(request):
    if 'email' in request.session:
        request.session.flush()
    logout(request)
    return redirect('home')
#cart
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cart(request):
    if 'discount' in request.session:
        del request.session['discount']
    user = request.user
    cart_items = Cart.objects.filter(user=user).order_by('id')
    subtotal = 0
    total_dict = {}
    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product.stock:
            messages.warning(request, f"{cart_item.product.product_name} is out of stock.")
            cart_item.quantity = cart_item.product.stock
            cart_item.save()
            item_price = Decimal(0) 
        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price
        elif cart_item.product.product_offer:
            item_price = (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price
        else:
            item_price = cart_item.product.price * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price # Initialize item price as a Decimal


    shipping_cost = 10
    total = subtotal + shipping_cost
    coupons = Coupon.objects.all()
    
    if 'discount' in request.session:
        discount = float(request.session['discount'])  # Convert discount to float
        total -= discount 
    for cart_item in cart_items:
        cart_item.total_price = total_dict.get(cart_item.id, 0)
        cart_item.save()
        print(cart_items,"........cart item")
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'coupons': coupons,   
    }
    return render(request, 'cart.html', context)
@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def add_to_cart(request,id ):
    try: 
         product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return redirect('product_not_found')
    quantity = request.POST.get('quantity', 1)
    if not quantity:
        quantity = 1
    else:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if created:
        cart_item.quantity = int(quantity)
    else:
        cart_item.quantity += int(quantity)
    cart_item.save()
    return redirect('cart')

def update_cart(request, productId):
    cart_item = None
    cart_item = get_object_or_404(Cart, product_id=productId, user=request.user)
    print(cart_item,"....................")
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity'))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'message': 'Invalid quantity.'}, status=400)
    if quantity < 1:
        return JsonResponse({'message': 'Quantity must be at least 1.'}, status=400)
    cart_item.quantity = quantity
    cart_item.save()
    return JsonResponse({'message': 'Cart item updated.'}, status=200)

@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def remove_from_cart(request,id):
    try:
        cart_item = Cart.objects.get(id=id, user=request.user)
        cart_item.delete()
    except Cart.DoesNotExist:
        pass
    return redirect('cart')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def checkout(request): 
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal = 0
    for cart_item in cart_items:
        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
            subtotal += item_price
        elif cart_item.product.product_offer:
            itemprice =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice = (cart_item.product.price) * (cart_item.quantity)
            subtotal = subtotal + itemprice
    shipping_cost = 10 
    discount = request.session.get('discount', 0)
    if discount:
        total =  subtotal + shipping_cost - discount if subtotal else 0    
    else:
        total =  subtotal + shipping_cost  if subtotal else 0
    addresses = Address.objects.filter(user=user)
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_amount'  :  discount,
        'total': total,
        'addresses': addresses,          
     }
    return render(request, 'checkout.html', context)

def shippingaddress(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        house_no = request.POST.get('house_no')
        post_code = request.POST.get('post_code')
        state = request.POST.get('state')
        street = request.POST.get('street')
        phone_no = request.POST.get('phone_no')
        city = request.POST.get('city')
        if not full_name or not house_no or not post_code or not state or not street or not phone_no or not city:
            messages.error(request, 'Please input all the details!!!')
            return redirect('checkout')  
        user = request.user  # Assuming you are using Django authentication and have a user object
        # Create and save the Address object
        address = Address.objects.create(
            user=user,
            full_name=full_name,
            house_no=house_no,
            post_code=post_code,
            state=state,
            street=street,
            phone_no=phone_no,
            city=city,
        )
        return redirect('checkout')  # Redirect to the appropriate URL after successful form submission
    else:
        # Render the form when the request method is not POST
        return render(request, 'checkout.html')  # Make sure to pass appropriate context data if needed
#placeorder
@login_required
def placeorder(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal=0
    for cart_item in cart_items:
        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
            subtotal += item_price
        elif cart_item.product.product_offer:
            itemprice =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice = (cart_item.product.price) * (cart_item.quantity)
            subtotal = subtotal + itemprice
    shipping_cost = 10 
    total = subtotal + shipping_cost if subtotal else 0
    discount = request.session.get('discount', 0)
    if request.method == 'POST':
        payment       =    request.POST.get('payment')
        address_id    =    request.POST.get('addressId')
    if not address_id:
        messages.info(request, 'Input Address!!!')
        return redirect('check_out')
    if discount:
        coupon=get_object_or_404(Coupon,discount_price=discount)

        # user_coupon_usage, created = UsedCoupon.objects.get_or_create(
        # user=user,coupon=coupon)
        user_coupon = UsedCoupon.objects.create(user = user , coupon=coupon,is_used = True)
        total -= discount
    address = Address.objects.get(id=request.POST.get('addressId'))
    order = Order.objects.create(
        user          =     user,
        address       =     address,
        amount        =     total,
        payment_type  =     payment,
    )
    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()
        order_item = OrderItem.objects.create(
            order         =     order,
            product       =     cart_item.product,
            quantity      =     cart_item.quantity,
            image         =     cart_item.product.image  
        )
    cart_items.delete()
    return redirect('success')
def success(request):
    orders = Order.objects.order_by('-id')[:1]
    context = {
        'orders'  : orders,
    }
    return render(request,'placeorder.html',context)

def restock_products(order):
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        product = order_item.product
        product.stock += order_item.quantity
        product.save()
#admin order management
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache     
def order(request):
    if 'admin' in request.session:
        orders = Order.objects.all().order_by('-id')
        paginator = Paginator(orders, per_page=10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'orders': page_obj,
        }
        return render(request, 'orders.html', context)
    else:
        return redirect('admin')

def updateorder(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return redirect('order') 
        # Check if the order status is already 'cancelled' and disallow changing it
        if order.status == 'cancelled':
            messages.error(request, 'Cancelled orders cannot have their status updated.')
            return redirect('order')

        order.status = new_status
        order.save()   
        messages.success(request, 'Order status updated successfully.')
        return redirect('order') 
    return redirect('admin')
#customer side order 
def customer_order(request):
    user = request.user 
    orders = Order.objects.filter(user = user).order_by('-id')
    print(orders)
    context ={
         'orders':orders,
        }
    return render(request,'customer_order.html',context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def order_details(request,id): 
    orders = Order.objects.filter(id=id)
    print(orders)
    context ={
         'orders':orders,
        }
    return render(request,'order_details.html',context)

def cancel_order(request, id):
    user=request.user
    usercustm=Customer.objects.get(email=user)
    order = Order.objects.get(id=id)
    if  order.status == 'completed' and  order.payment_type=='cod':
        wallet= Wallet.objects.create(
        user=user,
        order= order,
        amount= order.amount,
        status='Credited',
        )
        wallet.save()
        order.status='cancelled'
        order.save()
        Order_item_amount = Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        usercustm.save()
    elif  order.payment_type=='razorpay':
        wallet= Wallet.objects.create(
        user=user,
        order= order,
        amount= order.amount,
        status='Credited',
        )
        wallet.save()
        order.status='cancelled'
        order.save()
        Order_item_amount = Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        print('wallte:',usercustm.wallet_bal)
        usercustm.save()
    restock_products(order)
    order.status = 'cancelled'
    order.save()
    return redirect('order_details', id)

def return_order(request, id):
    user = request.user
    usercustm = Customer.objects.get(email=user)
    order = Order.objects.get(id=id)
    if (order.status == 'delivered' or order.status == 'completed') and (order.payment_type == 'cod' or order.payment_type == 'razorpay'):
        wallet = Wallet.objects.create(
            user=user,
            order=order,
            amount=order.amount,
            status='Credited'
        )
        wallet.save()
        order.status = 'returned'
        order.save()
        refund = Decimal(order.amount)
        usercustm.wallet_bal += refund
        usercustm.save()
        restock_products(order)
    
    return redirect('order_details', id)

#payment
def proceedtopay(request):
    print('hjbdshkbskdjg')
    cart = Cart.objects.filter(user=request.user)
    total = 0
    shipping = 10
    subtotal=0
    for cart_item in cart:
        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
            subtotal += item_price
        elif cart_item.product.product_offer:
            itemprice =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice = (cart_item.product.price) * (cart_item.quantity)
            subtotal = subtotal + itemprice
    for item in cart:
        discount = request.session.get('discount', 0)
    total=subtotal+shipping 
    if discount:
        total -= discount 
    return JsonResponse({
        'total' : total

    })

def razorpay(request,address_id):
    print("Razorrrrrrrrrrrrrrr pay")
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal=0
    for cart_item in cart_items:
        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
            subtotal += item_price
        elif cart_item.product.product_offer:
            itemprice =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice = (cart_item.product.price) * (cart_item.quantity)
            subtotal = subtotal + itemprice
    shipping_cost = 10 
    total = subtotal + shipping_cost if subtotal else 0
    
    discount = request.session.get('discount', 0)
    
    if discount:
        total -= discount 

    payment  =  'razorpay'
    user     = request.user
    cart_items = Cart.objects.filter(user=user)
    address = Address.objects.get(id=address_id)
    order = Order.objects.create(
        user          =     user,
        address       =     address,
        amount        =     total,
        payment_type  =     payment,
    )
    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()

        order_item = OrderItem.objects.create(
            order         =     order,
            product       =     cart_item.product,
            quantity      =     cart_item.quantity,
            image         =     cart_item.product.image  
        )
    
    cart_items.delete()
    return redirect('success')
def contact(request):
    context = {}  
    if request.method=='POST':
        user=request.user
        message = request.POST.get('message')
        
        # Save the message to the database
        contact = Contact(user=user,message=message)
        contact.save()
        messages.success(request,'Thank you for contacting us!')

        return redirect('contact') 
    return render(request,'contact.html',context)



def adminside_message(request):
    customer_messages=Contact.objects.all()
    context={
        'customer_messages':customer_messages
    }
    return render(request,'adminside_message.html',context)


def send_message(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        message_content = request.POST.get('message')

        subject = 'Reply from Our Site'
        from_email = 'stopnshop890@gmail.com'
        to_email = user_email

        # Create the MIME message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message_content, 'plain'))

        # try:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'stopnshop890@gmail.com'
        smtp_password = 'qoruttdlboezrrcc'
        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()

    messages.success(request, 'Email sent successfully.')
    return redirect('adminside_message')