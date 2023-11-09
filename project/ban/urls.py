from django.urls import path
from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # banner
    path('banner/',views.banner,name='banner'),
    path('add_banner/',views.add_banner,name='add_banner'),
    path('edit_banner/<int:banner_id>/',views.edit_banner,name='edit_banner'),
    path('update_banner/<int:banner_id>/',views.update_banner,name='update_banner'),
    path('delete_banner/<int:banner_id>/',views.delete_banner,name='delete_banner'),
     
    #invoice
    path('invoice/<int:id>',views.invoice,name='invoice'),

    #salesreprt
    path('report-pdf-order/', views.report_pdf_order, name='report_pdf_order'),
    path('chart-demo/', views.chart_demo, name='chart_demo'),

    #admin order search
    path('searchorder/',views.searchorder,name='searchorder'),
     #wishlist
    path('wishlist/',views.wishlist, name='wishlist'),
    path('addtowishlist/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:wishlist_item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
   
   #search
    path('search/',views.search,name='search'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    
    #wallet
    path('wallet/',views.wallet,name='wallet'),
     #coupon
    path('coupon/',views.coupon,name = 'coupon'),
    path('addcoupon/',views.addcoupon,name='addcoupon'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('coupon/<int:coupon_id>/edit/', views.editcoupon, name='edit_coupon'), 
    path('coupon/<int:id>/update_coupon/', views.update_coupon, name='update_coupon'),
    path('coupon/<int:coupon_id>/delete/', views.delete_coupon, name='delete_coupon'),

    #section
    path('section/',views.section, name = 'section'),
    path('addsection/',views.addsection,name= 'add_section'),
    path('section/<int:id>/update_section/', views.update_section, name='update_section'),
    path('section/<int:section_id>/delete/', views.delete_section, name='delete_section'),
    path('section/<int:section_id>/edit/', views.editsection, name='edit_section'),
     #subcategory
    path('subcategory/', views.subcategory, name='subcategory'),
    path('subcategory/<int:subcategory_id>/edit/', views.edit_sub_category, name='edit_subcategory'),
    path('subcategory/<int:subcategory_id>/delete/', views.delete_subcategory, name='delete_subcategory'),
    path('subcategory/<int:subcategory_id>/update/', views.update_sub_category, name='update_subcategory'),
    path('add_sub_category/', views.add_sub_category, name='addsub_category'),
     #category
    path('category/',views.category, name = 'category'),
    path('addc/',views.add_category,name= 'add_category'),
    path('category/<int:id>/update_category/', views.update_category, name='update_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/edit/', views.editcategory, name='edit_category'),
    #product
     path('products/',views.product,name='products'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/',views.editproduct,name='edit_product'),
    path('product/<int:id>/update/', views.update, name='update'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    

   

]