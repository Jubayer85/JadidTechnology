# myshop/context_processors.py
from .models import SiteSettings, Category, Brand, Cart

def cart_context(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_count = sum(item.quantity for item in cart.items.all())
        except:
            cart_count = 0
    return {'cart_count': cart_count}

def navbar_data(request):
    try:
        categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')
        brands = Brand.objects.filter(is_active=True, show_in_brands=True)
    except:
        categories = []
        brands = []
    
    return {
        "nav_categories": categories,
        "nav_brands": brands,
    }

def site_settings(request):
    """Add site settings to all templates"""
    try:
        settings = SiteSettings.objects.first()
        # Debug print
        if settings:
            print(f"[DEBUG] Site Settings loaded: {settings.site_name}")
            print(f"[DEBUG] Hero Enabled: {settings.hero_enabled}")
            print(f"[DEBUG] Logo exists: {bool(settings.site_logo)}")
        else:
            print("[DEBUG] No Site Settings found - please create from admin")
    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        settings = None
    
    return {'site_settings': settings}