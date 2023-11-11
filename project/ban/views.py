from django.shortcuts import render
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import cache_control, never_cache
from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from django.db.models import Count
from datetime import datetime
from .models import *
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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
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
from django.http import JsonResponse
from django.db.models import Q
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
from app.models import *
from reportlab.lib import colors

# Create your views here.
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def banner(request):
    if 'admin' in request.session:

        banner=Banner.objects.all()
        context = {

            'banner':banner,
    }
        return render(request,'banner.html',context)

    else:
        return redirect('admin')

def add_banner(request):
    if 'admin' in request.session:
            
        if request.method == 'POST':
            description = request.POST.get('description')
            image = request.FILES.get('image')
            banner = Banner(description=description, image=image)
            banner.save()
        
            return redirect('banner') 
        return render(request,'add_banner.html') 
    else:
        return redirect('admin')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def edit_banner(request, banner_id):
    if 'admin' in request.session:
        try:
            banner = Banner.objects.get(id=banner_id)
        except Banner.DoesNotExist:
        
            return render(request, 'product_not_found.html')
        
        
        context = {
            'banner': banner,
            
        }

        return render(request, 'edit_banner.html', context)
    else:
        return redirect('admin')
    

   
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_banner(request,banner_id):
    banner= Banner.objects.get(id=banner_id)

    if request.method == 'POST':
        
        banner.description = request.POST.get('description')
        image = request.FILES.get('image')

        if image:
            banner.image = image
        banner.save()
      
        return redirect('banner')
    else:
        context = {
            'banner': banner,
        }
        return render(request, 'banner.html', context)
    


def delete_banner(request,banner_id):
    print(banner_id)
    try:
        banner = Banner.objects.get(id=banner_id)
        banner.delete()
    except Banner.DoesNotExist:
        return render(request, 'category_not_found.html')

    
    return redirect('banner')

def invoice(request, id):
    # 1. Fetch the order and items
    user = request.user
    orders = Order.objects.filter(id=id)
    order_items = OrderItem.objects.filter(order=id)
    
    for order in orders:
        address = order.address
        for item in order_items:
            # 2. Render the order and items to an HTML template
            rendered = render_to_string('invoice.html', {'order': order, 'item': item ,'address': address,})

            # 3. Convert the rendered HTML to PDF
            output = io.BytesIO()
            pdf = pisa.CreatePDF(rendered, output)
            pdf_data = output.getvalue()

            # 4. Send the PDF as an email attachment
            msg = MIMEMultipart()
            msg['From'] = 'stopnshop890@gmail.com'
            msg['To'] = order.user.email
            msg['Subject'] = 'Invoice from Stop & Shop'

            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(pdf_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment; filename=invoice.pdf')
            msg.attach(attachment)

            try:
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                smtp_username = 'stopnshop890@gmail.com'
                smtp_password = 'qoruttdlboezrrcc'

                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                server.quit()

            except Exception as e:
                return HttpResponse(f'Email sending failed: {str(e)}')

    return HttpResponse('Emails sent successfully!')



def report_generator(request, orders):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    story = []

    data = [["Order ID", "Total Quantity", "Product IDs", "Product Names", "Amount"]]

    for order in orders:
        # Retrieve order items associated with the current order
        order_items = OrderItem.objects.filter(order=order)
        total_quantity = sum(item.quantity for item in order_items)

        if order_items.exists():
            product_ids = ", ".join([str(item.product.id) for item in order_items])
            product_names = ", ".join([str(item.product.product_name) for item in order_items])
        else:
            product_ids = "N/A"
            product_names = "N/A"

        data.append([order.id, total_quantity, product_ids, product_names, order.amount])

    # Create a table with the data
    table = Table(data, colWidths=[1 * inch, 1.5 * inch, 2 * inch, 3 * inch, 1 * inch])

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(table_style)

    # Add the table to the story and build the document
    story.append(table)
    doc.build(story)

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='orders_report.pdf')

def report_pdf_order(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse('Invalid date format.')
        orders = Order.objects.filter(date__range=[from_date, to_date]).order_by('-id')
        return report_generator(request, orders)


import json
def chart_demo(request):
    orders = Order.objects.order_by('-id')[:5]
    labels = []
    data = []
    for order in orders:
        labels.append(str(order.id))
        data.append(order.amount)
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }

    return render(request, 'chart_demo.html', context)

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def searchorder(request):
    # Get the 'q' parameter from the GET request
    query = request.GET.get('q', '')
    print(query)

    if query:
        # Perform a case-insensitive search on product names and descriptions
        orders = Order.objects.filter(
            models.Q(user__username__icontains=query) 
           
        )
        # Set search_results to products filtered by the query
        search_results = orders
        print(search_results,'jjdkssssss')
    

    context = {
        'orders': orders,
        'search_results': search_results,
    }

    return render(request, 'ordersearch.html', context)



#wishlist

def wishlist(request):

    user = request.user
    
    wishlist_items = Wishlist.objects.filter(user=user)
    context = {
        'wishlist_items': wishlist_items
    }

    return render(request, 'wishlist.html', context)


def add_to_wishlist(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return redirect('product_not_found')
    
    user = request.user
    # Unpack the tuple returned by get_or_create
    wishlist, created = Wishlist.objects.get_or_create(product=product, user=user)
    
    # Check if the object was created or retrieved
    if created:
        # If it was created, you might want to do something specific
        pass
    
    # Call save() on the Wishlist object, not on the tuple
    wishlist.save()

    return redirect('wishlist')


def remove_from_wishlist(request, wishlist_item_id):
    try:
        if request.user.is_authenticated:
            wishlist_item = Wishlist.objects.get(id=wishlist_item_id, user=request.user)
        wishlist_item.delete()
    except Wishlist.DoesNotExist:
        pass
    
    return redirect('wishlist')


def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(product_name__icontains=query)[:5]  # Limiting to 5 suggestions
        suggestions = [product.product_name for product in products]
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)

  # Import your Product model correctly


def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.select_related('category', 'section').all()
    products_with_offers = []  # This will hold our product dictionaries

    for product in products:
        # Calculate category offer and product offer
        category_offer = product.category.category_offer if product.category.category_offer else 0
        product_offer = product.product_offer if product.product_offer else 0

        # Calculate discount and offer prices
        discount_amount = (product.price * category_offer) / 100 if category_offer else 0
        offer_price_amount = (product.price * product_offer) / 100 if product_offer else 0

        # Use the highest priority offer
        final_price = product.price - max(discount_amount, offer_price_amount)

        # Create a dictionary for each product with all necessary data
        product_data = {
            'id': product.id,
            'product_name': product.product_name,
            'description': product.description,
             'category': product.category.category_name,  # Use the correct field name from the Category model
             'stock': product.stock,
             'price': product.price,
             'image_url': product.image.url,
             'section': product.section.name if product.section else '',  # Handling a possible None value
             'color': product.color,
             'product_offer': product_offer,
            'discounted_price': product.price - discount_amount if category_offer else None,
             'offer_price': product.price - offer_price_amount if product_offer else None,
             'final_price': final_price,
}
        products_with_offers.append(product_data)

    # If there's a query, filter the products list
    if query:
        products_with_offers = [
            product for product in products_with_offers
            if query.lower() in product['product_name'].lower() or query.lower() in product['description'].lower()
        ]

    context = {
        'products': products_with_offers,
    }

    # Now we render the template with the context containing product dictionaries
    return render(request, 'search.html', context)



def wallet(request):
    user=request.user
    customer=Customer.objects.get(email=user)
    wallets= Wallet.objects.filter(user=user).order_by('-created_at')
    # Assuming you have the 'wallet' object available
    context = {
        'customer':customer,
        'wallets': wallets,
    }
    return render(request, 'wallet.html', context)


#coupon
@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def coupon(request):
    if 'admin' in request.session:
        coupons = Coupon.objects.all().order_by('id')
        context = {'coupons': coupons}
        return render(request, 'coupon.html', context)
    else:
        return redirect('admin')

def addcoupon(request):
    if request.method == 'POST':
        coupon_code    = request.POST.get('Couponcode')
        discount_price  = request.POST.get('dprice')
        minimum_amount = request.POST.get('amount')
        expiry_date = request.POST.get('date')  
        coupon = Coupon(coupon_code=coupon_code, discount_price=discount_price, minimum_amount=minimum_amount,expiry_date=expiry_date)
        coupon.save()
        return redirect('coupon')
    
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code')
            return redirect('checkout')
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        subtotal = 0
        shipping_cost = 10
        total_dict = {}
        coupons = Coupon.objects.all()
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                messages.warning(request, f"{cart_item.product.product_name} is out of stock.")
                cart_item.quantity = cart_item.product.stock
                cart_item.save()
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
                subtotal += item_price
        if subtotal >= coupon.minimum_amount:
            messages.success(request, 'Coupon applied successfully')
            request.session['discount'] = coupon.discount_price
            print( request.session['discount'])
            total = subtotal - coupon.discount_price + shipping_cost
        else:
            messages.error(request, 'Coupon not available for this price')
            total = subtotal + shipping_cost
        for cart_item in cart_items:
            cart_item.total_price = total_dict.get(cart_item.id, 0)
            cart_item.save()
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'total': total,
            'coupons': coupons,
            'discount_amount': coupon.discount_price,
        }
        return render(request, 'cart.html', context)
    return redirect('cart')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editcoupon(request,coupon_id):
    if 'admin' in request.session:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Section.DoesNotExist:
            return render(request, 'subcategory_not_found.html')
        context = {'coupon': coupon}
        return render(request, 'edit_coupon.html', context)
    else:
        return redirect ('admin')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_coupon(request, id):
    # Use get_object_or_404 to retrieve the coupon or return a 404 page if it doesn't exist
    coupon = get_object_or_404(Coupon, id=id)
    if request.method == 'POST':
        coupon_code = request.POST.get('Couponcode')
        discount_price = request.POST.get('price')
        minimum_amount = request.POST.get('amount')
        expiry_date = request.POST.get('date')
        # Check if coupon_code and discount_price are not null before updating
        if coupon_code:
            coupon.coupon_code = coupon_code
        if discount_price:
            coupon.discount_price = discount_price
        coupon.minimum_amount = minimum_amount
        coupon.expiry_date = expiry_date
        coupon.save()  # Save the updated coupon object here
        return redirect('coupon')
    context = {'coupon': coupon}
    return render(request, 'edit_coupon.html', context)

def delete_coupon(request,coupon_id):
    try:
        coupon= Coupon.objects.get(id=coupon_id)
    except Coupon.DoesNotExist:
        return render(request, 'category_not_found.html')
    coupon.delete()
    coupons = Coupon.objects.all()
    context = {'coupons': coupons}
    return redirect('coupon')
#section
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def section(request):
    if 'admin' in request.session:
        sections = Section.objects.all().order_by('id')
        paginator = Paginator(sections, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'sections': page_obj,
        }
        return render(request, 'section.html', context)
    else:
        return redirect('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache          
def addsection(request):
    if 'admin' in request.session:
        if request.method  == 'POST':
            name   =   request.POST['name']
            section = Section.objects.create(
             name  =  name,     
            )
            section.save() 
            return redirect('section')  
        return render(request, 'add_section.html') 
    else:
        return redirect ('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editsection(request, section_id):
    if 'admin' in request.session:
        try:
            section = Section.objects.get(id=section_id)
        except Section.DoesNotExist:
            return render(request, 'subcategory_not_found.html')
        context = {'section': section}
        return render(request, 'edit_section.html', context)
    else:
        return redirect ('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update_section(request, id):
    try:
        section = Section.objects.get(id=id)
    except Section.DoesNotExist:
        return render(request, 'category_not_found.html')
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            section.name           =  name
        section.save()
        return redirect('section')
    context = {'section': section}
    return render(request, 'edit_section.html', context)

def delete_section(request,section_id):
    try:
        section = Section.objects.get(id=section_id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')
    section.delete()
    sections = Section.objects.all()
    context = {'sections': section}
    return redirect('section')

#category
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def category(request):
    if 'admin' in request.session:
        categories = Category.objects.all().order_by('id')
        paginator = Paginator(categories, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'categories': page_obj,
        }
        return render(request, 'category.html', context)
    else:
        return redirect('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache          
def add_category(request):
    if 'admin' in request.session:
        if request.method  == 'POST':
            category_name       =   request.POST['category_name']
            description         =   request.POST['description']
            offer_description   =   request.POST.get('offer_details', None)
            offer_price         =   request.POST.get('offer_price', None)
            # Check if offer_price is an empty string and set it to None
            if not offer_price:
                offer_price = None
            category = Category.objects.create(
                category_name                =  category_name,
                description                  =  description,
                category_offer_description   =  offer_description,
                category_offer               =  offer_price     
            )
            category.save() 
            return redirect('category')  
        return render(request, 'add_category.html') 
    else:
        return redirect ('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editcategory(request, category_id):
    if 'admin' in request.session:
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return render(request, 'subcategory_not_found.html')

        context = {'category': category}
        return render(request, 'edit_category.html', context)
    else:
        return redirect ('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update_category(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if category_name:
            category.category_name = category_name
        category.description = request.POST.get('description')
        category.category_offer_description = request.POST.get('offer_details')
        # Check for None or empty offer_price before assignment
        offer_price = request.POST.get('offer_price')
        if offer_price not in (None, '', 'None'):
            category.category_offer = int(offer_price)
        category.save()
        return redirect('category')
    context = {'category': category}
    return render(request, 'edit_category.html', context)

def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')
    category.delete()
    categories = Category.objects.all()
    context = {'categories': categories}
    return redirect('category')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def subcategory(request):
    if 'admin' in request.session:
        subcategories = Sub_category.objects.all()
        maincategories = Category.objects.all()
        maincategory_names = {}
        maincategory_ids = {}
        for sub in subcategories:
            maincategory_names[sub.id] = sub.main_category.category_name
            maincategory_ids[sub.id] = sub.main_category.id         
        paginator = Paginator(subcategories, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'categories': page_obj,
            'subcategories' : subcategories,
            'maincategories' :maincategories,
            'maincategory_names': maincategory_names,
            'maincategory_ids': maincategory_ids,
        }
        return render(request,'sub_category.html',context)
    else:
        return redirect('admin')
def add_sub_category(request):
    main_category=Category.objects.all()
    context={
        'main_category':main_category
    }
    if 'admin' in request.session: 
        if request.method  == 'POST':
            cat      = request.POST.get('categories')
            print(cat)
            sub_category_name   =request.POST.get('name')
            main = Category.objects.get(id=cat) 
            sub = Sub_category.objects.create(main_category=main,sub_category_name=sub_category_name)
            sub.save() 
            return redirect('subcategory')  
        return render(request,'add_subcategory.html',context)
    else:
        return redirect ('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def edit_sub_category(request,subcategory_id):
    cat = Category.objects.all()
    if 'admin' in request.session:
        try:
            sub_category =  Sub_category.objects.get(id=subcategory_id)
        except  Sub_category.DoesNotExist:
            return render(request, 'category_not_found.html')
        context = {'sub_category': sub_category,'cat':cat}
        return render(request, 'edit_subcategory.html', context)
    else:
        return redirect ('admin')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_sub_category(request,subcategory_id):
    main_category = Category.objects.all()
    sub_category = Sub_category.objects.get(id=subcategory_id)  # Use get() instead of filter()
    if request.method == 'POST':
        new_name = request.POST.get('sub_category_name')
        new_main_id = request.POST.get('main_category')
        sub_category.sub_category_name = new_name
        # sub_category.main_category_id = new_main_id
        sub_category.save()
        return redirect('subcategory')
    return render(request, 'edit_sub_category.html')

def delete_subcategory(request,subcategory_id):
    try:
        subcategory = Sub_category.objects.get(id=subcategory_id)
        print(subcategory , "......................")
    except Sub_category.DoesNotExist:
        return render(request,'category_not_found.html')
    subcategory.delete()
    return redirect('subcategory')
#products
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def product(request):
    if 'admin' in request.session:
        products = Product.objects.all().order_by('id')      
        paginator = Paginator(products, 3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
           
        }
        return render(request, 'product.html', context)
    else:
        return redirect('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def add_product(request):
    if 'admin' in request.session:
        if request.method == 'POST':
            product_name = request.POST.get('product_name')
            description = request.POST.get('description')
            category_name = request.POST.get('category')
            name = request.POST.get('section')
            category = get_object_or_404(Category, category_name=category_name)
            section = get_object_or_404(Section, name=name)
            stock = request.POST.get('stock')
            offer = request.POST.get('offer')
            price = request.POST.get('price')
            color = request.POST.get('color')
            image = request.FILES.get('image')
            images = request.FILES.getlist('mulimage')
            if not (product_name and description and category_name and price and image):
                error_message = "Please fill in all the required fields."
                categories = Category.objects.all()
                context = {'categories': categories, 'error_message': error_message}
                return render(request, 'add_product.html', context)
            product = Product()
            product.product_name = product_name
            product.description = description
            product.category = category
            product.section = section
            product.stock = stock
            # Handling potentially empty or None offer
            if not offer:  # Checks for empty string, None, and other falsy values
                product.product_offer = None
            else:
                product.product_offer = int(offer)
            product.price = price
            product.color = color
            product.image = image
            product.save()
            for img in images:
                Images.objects.create(product=product, images=img)
            return redirect('products')
        categories = Category.objects.all()
        sections = Section.objects.all()
        context = {
            'categories': categories,
            'sections': sections
        }
        return render(request, 'add_product.html', context)
    else:
        return redirect('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editproduct(request, product_id):
    if 'admin' in request.session:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
        
            return render(request, 'product_not_found.html')
        categories = Category.objects.all()
        sections=Section.objects.all()
        context = {
            'product'    : product,
            'categories' : categories,
            'sections'   :sections,
        }
        return render(request, 'editproduct.html', context)
    else:
        return redirect('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.description = request.POST.get('description')
        if request.POST.get('category'):
            category_name = request.POST.get('category')
            category = Category.objects.get(category_name=category_name)
            product.category = category
        # Fetch the Section instance based on the section name
        if request.POST.get('section'):
            section_name = request.POST.get('section')
            try:
                section = Section.objects.get(name=section_name)
                product.section = section
            except Section.DoesNotExist:
                # Handle the case where the section does not exist
                return HttpResponse("Section not found")
        product.color = request.POST.get('color')
        product.stock = request.POST.get('stock')
        product.product_offer   =   request.POST.get('offer')
        product.price = request.POST.get('price')
        image = request.FILES.get('image')
        if image:
            product.image = image
        product.save()
        mul_image=request.FILES.getlist('images')
        if mul_image:
            for image in mul_image:
                im = Images(product=product, images=image)
                im.save()
        return redirect('products')
    else:
        context = {
            'product': product,
        }
    return render(request, 'product.html', context)

@user_passes_test(lambda u: u.is_staff, login_url='admin')
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return render(request, 'category_not_found.html')

    product.delete()

    return redirect('products')





