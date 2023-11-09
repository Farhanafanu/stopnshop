from django.urls import path
from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('base', views.base, name='base'),
    path('', views.home, name='home'),
   
    path('account/register',views.register,name='handleregister'),
    path('account/login',views.loginhome,name='handlelogin'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    path('accounts/',include('django.contrib.auth.urls')),
    
    #admin login
    path('adminn/', views.admin_login,name='admin'),
    path ('admin_logout/',views.admin_logout,name='admin_logout'),
    
    
    #customer
    path('customer/<int:customer_id>/block/', views.block_customer, name='block_customer'),
    path('customer/<int:customer_id>/unblock/', views.unblock_customer, name='unblock_customer'),
    
#dashboard,customer,order,product
    path('dashboard/', views.dashboard,name='dashboard'),
    path('Customer/',views.customers,name='customer'),
   
    #frontend
    path('shop/',views.shop,name='shop'),
    path('userproduct/<int:id>/',views.userproductpage,name='userproduct'),
    path('verify_otp/',views.verify_signup,name='verify_signup'),

    #userprofile
    path('profile/',views.profile,name='profile'),
    path('update_profile/',views.update_profile,name='update_profile'),
    path('changepassword/',views.changepassword,name='changepassword'),


   #address
    path('address/',views.address,name='address'),
    path('add_address/',views.add_address,name='add_address'),
    path('edit_address/<int:id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:id>/', views.delete_address, name='delete_address'),
    path('userlogout/',views.userlogout,name='userlogout'),

    #cart
    path('cart/',views.cart,name='cart'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:productId>/', views.update_cart, name='update_cart'),

    #checkout
    path('checkout',views.checkout,name='checkout'),
    path('shippingaddress/', views.shippingaddress, name='shippingaddress'),

    #placeorder
    path('placeorder/',views.placeorder,name='placeorder'),
    path('success/',views.success,name='success'),
   

    #order
    path('order/',views.order,name = 'order'),
    path('update_order/', views.updateorder, name='update_order'),
    

   #userside order
    path('cancel-order/<int:id>/', views.cancel_order, name='cancel_order'),
    path('return-order/<int:id>/', views.return_order, name='return_order'),
    path('customerorder/',views.customer_order,name = 'customer_order'),
    path('order_details/<int:id>',views.order_details,name='order_details'),


   

    #razorpay
    path('proceed-to-pay',views.proceedtopay,name='proceedtopay'),
    path('razorpay/<int:address_id>/',views.razorpay,name='razorpay'),

    # contact
    path('contact/',views.contact,name='contact'),
    path('adminside_message/',views.adminside_message,name='adminside_message'),
    path('reply/',views. send_message,name='send_message'),

    # path('ajax_search/', views.ajax_search, name='ajax_search'),
    





    
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)