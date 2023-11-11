from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from .manager import UserManager 
from datetime import date
# Import the UserManager class from the appropriate location


# Create your models here.

class Customer(AbstractUser):
    username           = models.CharField(null=True, blank=True, max_length=150)
    email              = models.EmailField(unique=True)
    number             = models.CharField(max_length=10)
    is_verified        = models.BooleanField(default=False)
    email_token        = models.CharField(max_length=100, null=True, blank=True)
    forgot_password    = models.CharField(max_length=100, null=True, blank=True)
    last_login_time    = models.DateTimeField(null=True, blank=True)
    last_logout_time   = models.DateTimeField(null=True, blank=True)
    profile_photo      = models.ImageField(upload_to='products', null=True, blank=True)
    referral_code      = models.CharField(max_length=100, null=True, unique=True)
    referral_amount    = models.IntegerField(default=0)
    wallet_bal= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Specify the related_name for the groups and user_permissions fields.
    groups = models.ManyToManyField(Group, related_name='customers')
    user_permissions = models.ManyToManyField(Permission, related_name='customers')

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, default='')
    image = models.ImageField(upload_to='products')
    category_offer_description = models.CharField(max_length=100, null=True, blank=True)
    
    category_offer = models.PositiveBigIntegerField(default=0,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
 
class Section(models.Model) :
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, default='')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock    = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products')
    section=models.ForeignKey(Section,on_delete=models.CASCADE,blank=True,null=True)
    color=models.CharField(max_length=100,null=True,blank=True)
    product_offer  = models.PositiveBigIntegerField(default=0,null=True, blank=True)



class Images(models.Model):
    product     =  models.ForeignKey(Product, on_delete=models.CASCADE)
    images      =  models.ImageField(upload_to='products')

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=200)
    image = models.ForeignKey(Images,on_delete=models.CASCADE , null=True , blank=True)
    price =models.IntegerField(blank=True , null=True)
     
    
class Sub_category(models.Model):
    Sub_category_id=models.CharField(default=0,max_length=100)
    main_category=models.ForeignKey(Category,on_delete=models.CASCADE)
    sub_category_name=models.CharField(max_length=100)



    

class Address(models.Model):
    user=models.ForeignKey(Customer,on_delete=models.CASCADE,null=True,blank=True)
    full_name =models.CharField(max_length=100,default='')
    house_no  =models.CharField(max_length=100,default='')
    post_code =models.CharField(max_length=20,default='')
    state     =models.CharField(max_length=50,default='')
    street    =models.CharField(max_length=100,default='')
    phone_no  =models.CharField(max_length=15,blank=True)
    city      =models.CharField(max_length=100,default='')
    is_default = models.BooleanField(default=False) 

class Wishlist(models.Model):
    user          =     models.ForeignKey(Customer,on_delete=models.CASCADE,null = True,blank=True)
    product       =     models.ForeignKey(Product,on_delete=models.CASCADE)
    image         =     models.ImageField(upload_to='products',null = True,blank=True)
    

    def __str__(self):
        return f"Wishlist:{self.user.username}-{self.product}"

class Cart(models.Model):
    user           =     models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True)
    product        =     models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True)
    quantity       =     models.IntegerField(default=0)
    image          =     models.ImageField(upload_to='products',null=True, blank=True )
    
    @property
    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
          return f"Cart: {self.user.username} - {self.product} - Quantity: {self.quantity}"



class Order(models.Model):

    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing','processing'),
        ('shipped','shipped'),
        ('delivered','delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('returned', 'returned'),
        ('refunded','refunded'),
        ('on_hold','on_hold')

    )

    user           =   models.ForeignKey(Customer, on_delete=models.CASCADE) 
    address        =   models.ForeignKey(Address, on_delete=models.CASCADE)
    product        =   models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    amount         =   models.CharField(max_length=100)  
    payment_type   =   models.CharField(max_length=100)  
    status         =   models.CharField(max_length=100, choices=ORDER_STATUS, default='pending' )  
    quantity       =   models.IntegerField(default=0, null=True, blank=True)
    image          =   models.ImageField(upload_to='products', null=True, blank=True)
    date           =   models.DateField(default=date.today)
    
    def __str__(self):
        return f"Order #{self.pk} - {self.product}"

class OrderItem(models.Model):
    order          =   models.ForeignKey(Order,on_delete=models.CASCADE)
    product        =   models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity       =   models.IntegerField(default=1)
    image          =   models.ImageField(upload_to='products', null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
class Coupon(models.Model):
    coupon_code     =  models.CharField(max_length=100)
    expired         =  models.BooleanField(default=False)
    discount_price  =  models.PositiveIntegerField(default=100)
    minimum_amount  =  models.PositiveIntegerField(default=500)
    expiry_date     =  models.DateField(null=True,blank=True)
    user            =  models.ManyToManyField(Customer,blank=True)


    def __str__(self):
        return self.coupon_code

class Wallet(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_credit = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,blank=True)

    def _str_(self):
        return f"{self.amount} {self.is_credit}"

    def _iter_(self):
        yield self.pk
class Contact(models.Model):
    user  =models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True)
    message = models.CharField(max_length=1000, null=True, blank=True)

class UsedCoupon(models.Model):
    user        =models.ForeignKey(Customer,on_delete=models.CASCADE)
    coupon      =models.ForeignKey(Coupon,on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)

    def _str_(self):
        return f"{self.user.name} - {self.coupon.coupon_code}"