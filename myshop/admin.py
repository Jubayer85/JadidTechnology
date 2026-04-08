from django.contrib import admin
from .models import Product
from django import forms
from .models import SiteSettings
from django.urls import path
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import (
    Brand,
    Category,
    Product,
    ProductImage,
    Customer,
    Order,
    OrderItem,
    Cart,
    CartItem,
)




class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ['logo', 'favicon', 'site_name']
        widgets = {
            'logo': forms.FileInput(attrs={'accept': 'image/*'}),
            'favicon': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    fieldsets = (
        ('Logo & Branding', {
            'fields': ('logo', 'favicon', 'site_name'),
            'description': 'Upload your site logo (recommended size: 200x60px, PNG with transparency)'
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-logo/', self.admin_site.admin_view(self.upload_logo), name='upload_logo'),
        ]
        return custom_urls + urls
    
    def upload_logo(self, request):
        if request.method == 'POST' and request.FILES.get('logo'):
            site_settings = SiteSettings.objects.first()
            if not site_settings:
                site_settings = SiteSettings.objects.create()
            site_settings.logo = request.FILES['logo']
            site_settings.save()
            messages.success(request, 'Logo uploaded successfully!')
            return redirect('admin:index')
        return render(request, 'admin/upload_logo.html')

admin.site.register(SiteSettings, SiteSettingsAdmin)

# ======================================================
# Product Image Inline
# ======================================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# ======================================================
# Product Admin
# ======================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'is_active', 'stock_quantity', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'brand', 'category']
    list_editable = ['is_active', 'stock_quantity', 'price']  # Optional: quick edit
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    ordering = ('-created_at',)


# ======================================================
# Brand Admin
# ======================================================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'show_in_brands', 'is_featured', 'tier')
    list_filter = ('is_active', 'show_in_brands', 'is_featured', 'tier')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# ======================================================
# Category Admin
# ======================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# ======================================================
# Product Image Admin
# ======================================================
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'created_at')
    list_filter = ('created_at',)


# ======================================================
# Customer Admin
# ======================================================
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user__username', 'user__email')


# ======================================================
# Order Admin
# ======================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'customer',
        'status',
        'total_amount',
        'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'customer__user__username')


# ======================================================
# Order Item Admin
# ======================================================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product_name',
        'quantity',
        'total_price',
    )
    search_fields = ('product_name',)
    list_filter = ('order',)


# ======================================================
# Cart Item Inline (inside Cart)
# ======================================================
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'quantity', 'subtotal')
    raw_id_fields = ('product',)

    def subtotal(self, obj):
        return f"৳{obj.subtotal()}"
    subtotal.short_description = 'Subtotal'


# ======================================================
# Cart Admin
# ======================================================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'item_count',
        'cart_total',
        'created_at',
        'updated_at',
    )
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    def cart_total(self, obj):
        return f"৳{obj.total_price()}"
    cart_total.short_description = 'Total'


# ======================================================
# Cart Item Admin (ONLY ONE REGISTRATION)
# ======================================================
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'cart',
        'product',
        'quantity',
        'subtotal',
        'added_at',
    )
    list_filter = ('added_at', 'cart__user')
    search_fields = ('product__name', 'cart__user__username')
    readonly_fields = ('subtotal', 'added_at')
    raw_id_fields = ('product', 'cart')

    def subtotal(self, obj):
        return f"৳{obj.subtotal()}"
    subtotal.short_description = 'Subtotal'
