from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
import os
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
import random
import string
from decimal import Decimal
import time  # ✅ time module যোগ করুন
from django.utils.html import format_html


class HeroSlide(models.Model):
    """Individual hero slide for slider"""
    
    # Existing fields...
    title = models.CharField(max_length=200, default='Premium Smartphones', verbose_name="Slide Title")
    highlight_text = models.CharField(max_length=100, blank=True, verbose_name="Highlight Text")
    subtitle = models.TextField(default='Cutting-edge technology with exceptional performance.', verbose_name="Subtitle")
    
    # Font Size Controls
    title_font_size = models.IntegerField(default=48, help_text="Title font size in pixels", verbose_name="Title Font Size")
    highlight_font_size = models.IntegerField(default=36, help_text="Highlight text font size in pixels", verbose_name="Highlight Font Size")
    subtitle_font_size = models.IntegerField(default=20, help_text="Subtitle font size in pixels", verbose_name="Subtitle Font Size")
    
    # Badge
    badge_text = models.CharField(max_length=100, blank=True, verbose_name="Badge Text")
    badge_icon = models.CharField(max_length=50, default='fire', verbose_name="Badge Icon")
    badge_color = models.CharField(max_length=50, default='accent', verbose_name="Badge Color")
    badge_color_2 = models.CharField(max_length=50, default='brand', verbose_name="Badge Color 2")
    
    # Images
    image = models.ImageField(upload_to='hero/slides/', blank=True, null=True, verbose_name="Slide Image")
    
    # ========== IMAGE SIZE & STYLE CONTROLS ==========
    
    # Image Size Options
    IMAGE_WIDTH_CHOICES = [
        ('auto', 'Auto (Original)'),
        ('100%', 'Full Width (100%)'),
        ('90%', '90%'),
        ('80%', '80%'),
        ('70%', '70%'),
        ('60%', '60%'),
        ('50%', '50%'),
        ('40%', '40%'),
        ('300px', '300px'),
        ('350px', '350px'),
        ('400px', '400px'),
        ('450px', '450px'),
        ('500px', '500px'),
        ('550px', '550px'),
        ('600px', '600px'),
    ]
    
    IMAGE_HEIGHT_CHOICES = [
        ('auto', 'Auto (Original)'),
        ('200px', '200px'),
        ('250px', '250px'),
        ('300px', '300px'),
        ('350px', '350px'),
        ('400px', '400px'),
        ('450px', '450px'),
        ('500px', '500px'),
        ('100%', '100%'),
    ]
    
    IMAGE_FIT_CHOICES = [
        ('cover', 'Cover (Fill & Crop)'),
        ('contain', 'Contain (Keep Ratio)'),
        ('fill', 'Fill (Stretch)'),
        ('scale-down', 'Scale Down'),
        ('none', 'None (Original)'),
    ]
    
    IMAGE_BORDER_CHOICES = [
        ('0', 'None (Sharp)'),
        ('0.25rem', 'Very Small (4px)'),
        ('0.5rem', 'Small (8px)'),
        ('0.75rem', 'Medium Small (12px)'),
        ('1rem', 'Medium (16px)'),
        ('1.25rem', 'Medium Large (20px)'),
        ('1.5rem', 'Large (24px)'),
        ('2rem', 'Extra Large (32px)'),
        ('50%', 'Circle (50%)'),
    ]
    
    IMAGE_POSITION_CHOICES = [
        ('center center', 'Center'),
        ('center top', 'Top Center'),
        ('center bottom', 'Bottom Center'),
        ('left center', 'Left Center'),
        ('right center', 'Right Center'),
        ('left top', 'Top Left'),
        ('right top', 'Top Right'),
        ('left bottom', 'Bottom Left'),
        ('right bottom', 'Bottom Right'),
    ]
    
    image_width = models.CharField(max_length=20, choices=IMAGE_WIDTH_CHOICES, default='auto', verbose_name="Image Width")
    image_height = models.CharField(max_length=20, choices=IMAGE_HEIGHT_CHOICES, default='auto', verbose_name="Image Height")
    image_object_fit = models.CharField(max_length=20, choices=IMAGE_FIT_CHOICES, default='cover', verbose_name="Object Fit")
    image_border_radius = models.CharField(max_length=20, choices=IMAGE_BORDER_CHOICES, default='1rem', verbose_name="Border Radius")
    image_position = models.CharField(max_length=30, choices=IMAGE_POSITION_CHOICES, default='center center', verbose_name="Image Position")
    image_shadow = models.BooleanField(default=True, verbose_name="Add Shadow Effect")
    image_shadow_size = models.CharField(max_length=20, default='lg', choices=[
        ('sm', 'Small Shadow'),
        ('md', 'Medium Shadow'),
        ('lg', 'Large Shadow'),
        ('xl', 'Extra Large Shadow'),
        ('none', 'No Shadow'),
    ], verbose_name="Shadow Size")
    image_hover_effect = models.BooleanField(default=True, verbose_name="Hover Scale Effect")
    image_hover_scale = models.DecimalField(max_digits=3, decimal_places=2, default=1.05, help_text="1.05 = 5% zoom", verbose_name="Hover Scale")
    image_opacity = models.IntegerField(default=100, help_text="0 to 100", verbose_name="Image Opacity (%)")
    image_custom_class = models.CharField(max_length=100, blank=True, verbose_name="Custom CSS Class")
    
    # Mobile specific image settings
    image_mobile_width = models.CharField(max_length=20, choices=IMAGE_WIDTH_CHOICES, default='80%', verbose_name="Mobile Image Width")
    image_mobile_height = models.CharField(max_length=20, choices=IMAGE_HEIGHT_CHOICES, default='auto', verbose_name="Mobile Image Height")
    
    # Buttons
    button1_text = models.CharField(max_length=50, default='Shop Now', verbose_name="Button 1 Text")
    button1_url = models.CharField(max_length=200, default='/shop/', verbose_name="Button 1 URL")
    button1_icon = models.CharField(max_length=50, default='shopping-cart', verbose_name="Button 1 Icon")
    button1_color = models.CharField(max_length=50, default='brand', verbose_name="Button 1 Color")
    button1_color_2 = models.CharField(max_length=50, default='brand-dark', verbose_name="Button 1 Color 2")
    
    button2_text = models.CharField(max_length=50, blank=True, verbose_name="Button 2 Text")
    button2_url = models.CharField(max_length=200, blank=True, verbose_name="Button 2 URL")
    button2_icon = models.CharField(max_length=50, default='star', verbose_name="Button 2 Icon")
    button2_color = models.CharField(max_length=50, default='accent', verbose_name="Button 2 Color")
    
    # Price Tag
    price_tag = models.CharField(max_length=50, blank=True, verbose_name="Price Tag")
    price_label = models.CharField(max_length=50, default='From', verbose_name="Price Label")
    price_tag_color = models.CharField(max_length=50, default='brand', verbose_name="Price Tag Color")
    price_tag_color_2 = models.CharField(max_length=50, default='brand-dark', verbose_name="Price Tag Color 2")
    
    # Badge (corner badge)
    badge = models.CharField(max_length=100, blank=True, verbose_name="Corner Badge")
    
    # Rating
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True, verbose_name="Rating")
    
    # Features (JSON field for multiple features)
    features = models.JSONField(default=list, blank=True, verbose_name="Features")
    
    # ========== NEW FIELDS FOR INDIVIDUAL SLIDE DESIGN ==========
    
    # Layout & Design Styles
    LAYOUT_CHOICES = [
        ('default', 'Default (Original Design)'),
        ('centered', 'Centered Layout'),
        ('split', 'Split Screen (Image + Text)'),
        ('fullscreen', 'Full Screen Overlay'),
        ('minimal', 'Minimal Design'),
        ('card', 'Card Style'),
        ('hero', 'Hero Bold'),
        ('gradient', 'Gradient Overlay'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('glass', 'Glassmorphism'),
        ('neon', 'Neon Glow'),
        ('gradient', 'Gradient Theme'),
        ('none', 'None (No Theme)'),
    ]
    
    ALIGNMENT_CHOICES = [
        ('left', 'Left Aligned'),
        ('center', 'Center Aligned'),
        ('right', 'Right Aligned'),
    ]
    
    ANIMATION_CHOICES = [
        ('fadeInUp', 'Fade In Up'),
        ('fadeIn', 'Fade In'),
        ('zoomIn', 'Zoom In'),
        ('slideInLeft', 'Slide In Left'),
        ('slideInRight', 'Slide In Right'),
        ('bounce', 'Bounce'),
        ('flipInX', 'Flip In X'),
        ('rotateIn', 'Rotate In'),
        ('lightSpeedIn', 'Light Speed In'),
        ('none', 'No Animation'),
    ]
    
    # Design Configuration
    layout_style = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='default', verbose_name="Layout Style")
    theme_style = models.CharField(max_length=20, choices=THEME_CHOICES, default='light', verbose_name="Theme Style")
    content_alignment = models.CharField(max_length=10, choices=ALIGNMENT_CHOICES, default='left', verbose_name="Content Alignment")
    animation_effect = models.CharField(max_length=30, choices=ANIMATION_CHOICES, default='fadeInUp', verbose_name="Animation Effect")
    
    # Custom Colors for this slide (override global settings)
    slide_bg_color = models.CharField(max_length=20, blank=True, null=True, verbose_name="Slide Background Color")
    slide_text_color = models.CharField(max_length=20, blank=True, null=True, verbose_name="Slide Text Color")
    slide_accent_color = models.CharField(max_length=20, blank=True, null=True, verbose_name="Slide Accent Color")
    slide_overlay_opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.5, help_text="0 to 1", verbose_name="Overlay Opacity")
    
    # Additional Images for Split Layout
    side_image = models.ImageField(upload_to='hero/side_images/', blank=True, null=True, verbose_name="Side Image (for Split Layout)")
    background_pattern = models.CharField(max_length=100, blank=True, null=True, verbose_name="Background Pattern")
    
    # Custom CSS Class
    custom_css_class = models.CharField(max_length=100, blank=True, verbose_name="Custom CSS Class")
    
    # Animation Delays for different elements
    title_delay = models.IntegerField(default=100, help_text="Delay in ms", verbose_name="Title Animation Delay")
    subtitle_delay = models.IntegerField(default=200, help_text="Delay in ms", verbose_name="Subtitle Animation Delay")
    button_delay = models.IntegerField(default=300, help_text="Delay in ms", verbose_name="Button Animation Delay")
    
    # Order & Status
    order = models.IntegerField(default=0, verbose_name="Display Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"
    
    def __str__(self):
        return self.title
    
    def get_feature_list(self):
        """Get features as list of dicts"""
        if isinstance(self.features, list):
            return self.features
        return []
    
    def get_image_style(self):
        """Get image container style as string"""
        styles = []
        
        if self.image_width != 'auto':
            styles.append(f"width: {self.image_width}")
        
        if self.image_height != 'auto':
            styles.append(f"height: {self.image_height}")
        
        if self.image_border_radius != '0':
            styles.append(f"border-radius: {self.image_border_radius}")
        
        if self.image_opacity < 100:
            styles.append(f"opacity: {self.image_opacity / 100}")
        
        return '; '.join(styles)
    
    def get_image_class(self):
        """Get image CSS classes"""
        classes = []
        
        if self.image_shadow:
            shadow_map = {
                'sm': 'shadow-sm',
                'md': 'shadow-md',
                'lg': 'shadow-lg',
                'xl': 'shadow-xl',
                'none': ''
            }
            if self.image_shadow_size in shadow_map and shadow_map[self.image_shadow_size]:
                classes.append(shadow_map[self.image_shadow_size])
        
        if self.image_hover_effect:
            classes.append('hover-scale')
        
        if self.image_custom_class:
            classes.append(self.image_custom_class)
        
        return ' '.join(classes)
    
    def get_button1_color(self):
        """Get button 1 color"""
        if self.button1_color == 'brand':
            return 'var(--primary-color)'
        elif self.button1_color == 'accent':
            return 'var(--accent-color)'
        return self.button1_color or 'var(--primary-color)'
    
    def get_button2_color(self):
        """Get button 2 color"""
        if self.button2_color == 'brand':
            return 'var(--primary-color)'
        elif self.button2_color == 'accent':
            return 'var(--accent-color)'
        return self.button2_color or 'var(--accent-color)'
    
    def get_slide_bg(self):
        """Get slide background style"""
        if self.slide_bg_color:
            return self.slide_bg_color
        if self.theme_style == 'dark':
            return '#1f2937'
        elif self.theme_style == 'light':
            return '#ffffff'
        return None
    
    def get_slide_text_color(self):
        """Get slide text color"""
        if self.slide_text_color:
            return self.slide_text_color
        if self.theme_style == 'dark':
            return '#ffffff'
        elif self.theme_style == 'light':
            return '#1f2937'
        return None
    
    def get_mobile_image_width(self):
        """Get mobile image width"""
        return self.image_mobile_width if self.image_mobile_width else self.image_width
    
    def get_mobile_image_height(self):
        """Get mobile image height"""
        return self.image_mobile_height if self.image_mobile_height else self.image_height


class SiteSettings(models.Model):
    """Dynamic site settings for admin control"""
     # ================= SITE BASIC INFO =================
    site_name = models.CharField(max_length=100, default='Jadid Technology', verbose_name="Site Name")
    site_tagline = models.CharField(max_length=200, blank=True, default='Premium Tech Store', verbose_name="Site Tagline")
    site_logo = models.ImageField(upload_to='site/logo/', blank=True, null=True, verbose_name="Site Logo")
    site_favicon = models.ImageField(upload_to='site/favicon/', blank=True, null=True, verbose_name="Favicon Icon")
    
    # Logo Settings
    logo_height = models.PositiveIntegerField(default=50, help_text="Logo height in pixels (30-100)", verbose_name="Logo Height (px)")
    logo_alignment = models.CharField(
        max_length=20,
        choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')],
        default='left',
        verbose_name="Logo Alignment"
    )
    
    # ================= TOP BAR SETTINGS (Section 1) =================
    show_top_bar = models.BooleanField(default=True, verbose_name="Show Top Bar")
    top_bar_text = models.CharField(max_length=500, blank=True, default='🚚 Free Shipping on orders over $50 | 24/7 Customer Support', verbose_name="Top Bar Text")
    top_bar_bg_color = models.CharField(max_length=20, default='#1f2937', verbose_name="Top Bar Background Color")
    top_bar_text_color = models.CharField(max_length=20, default='#ffffff', verbose_name="Top Bar Text Color")
    top_bar_font_size = models.CharField(
        max_length=10,
        choices=[('xs', 'Extra Small'), ('sm', 'Small'), ('base', 'Normal')],
        default='xs',
        verbose_name="Top Bar Font Size"
    )
    
    # ================= MIDDLE BAR SETTINGS (Section 2 - Main Header) =================
    middle_header_bg_color = models.CharField(max_length=20, default='#ffffff', verbose_name="Middle Bar Background Color")
    header_padding_y = models.PositiveIntegerField(default=12, help_text="Vertical padding in pixels (4-32)", verbose_name="Header Vertical Padding (px)")
    header_sticky = models.BooleanField(default=True, verbose_name="Sticky Header")
    search_style = models.CharField(
        max_length=20,
        choices=[('rounded', 'Rounded'), ('pill', 'Pill Shape'), ('square', 'Square')],
        default='rounded',
        verbose_name="Search Bar Style"
    )
    header_border = models.CharField(
        max_length=20,
        choices=[('none', 'None'), ('light', 'Light Border'), ('dark', 'Dark Border'), ('colored', 'Colored Border')],
        default='light',
        verbose_name="Header Border Style"
    )
    
    # ================= NAVIGATION BAR SETTINGS (Section 3) =================
    show_nav_bar = models.BooleanField(default=True, verbose_name="Show Navigation Bar")
    nav_bar_bg_color = models.CharField(max_length=20, default='#f8fafc', verbose_name="Navigation Bar Background Color")
    nav_link_color = models.CharField(max_length=20, default='#374151', verbose_name="Navigation Link Color")
    nav_hover_color = models.CharField(max_length=20, default='#4f46e5', verbose_name="Navigation Hover Color")
    nav_bar_height = models.PositiveIntegerField(default=48, help_text="Navigation bar height in pixels (36-80)", verbose_name="Nav Bar Height (px)")
    nav_layout = models.CharField(
        max_length=20,
        choices=[('left', 'Left Aligned'), ('center', 'Center Aligned'), ('between', 'Space Between')],
        default='left',
        verbose_name="Navigation Layout"
    )
    nav_sticky = models.BooleanField(default=False, verbose_name="Sticky Navigation Bar")
    
    # ================= LEGACY HEADER SETTINGS (Keep for backward compatibility) =================
    header_bg_color = models.CharField(max_length=20, default='#ffffff', verbose_name="Header Background Color (Legacy)")
    header_text_color = models.CharField(max_length=20, default='#1f2937', verbose_name="Header Text Color (Legacy)")
    header_height = models.PositiveIntegerField(default=70, help_text="Header height in pixels (50-150)", verbose_name="Header Height (px) - Legacy")
    header_layout = models.CharField(
        max_length=20,
        choices=[
            ('standard', 'Standard (Logo left, nav right)'),
            ('centered', 'Centered (Logo center)'),
            ('compact', 'Compact (Reduced padding)')
        ],
        default='standard',
        verbose_name="Header Layout Style (Legacy)"
    )
    
    # Hero Section Settings
    hero_enabled = models.BooleanField(default=True, verbose_name="Enable Hero Section")
    hero_title = models.CharField(max_length=200, default='Welcome to Jadid Technology', verbose_name="Hero Title")
    hero_highlight = models.CharField(max_length=100, blank=True, default='Best Deals', verbose_name="Hero Highlight")
    hero_subtitle = models.TextField(default='Discover the latest smartphones, laptops, and gadgets at best prices', verbose_name="Hero Subtitle")
    hero_button_text = models.CharField(max_length=50, default='Shop Now', verbose_name="Hero Button Text")
    hero_button_url = models.CharField(max_length=200, default='/shop/', verbose_name="Hero Button URL")
    hero_bg_color = models.CharField(max_length=20, default='#6366f1', verbose_name="Hero Background Color")
    
    # NEW: Hero Height & Slideshow Speed
    hero_height = models.PositiveIntegerField(default=500, help_text="Hero section height in pixels (300-800)", verbose_name="Hero Height (px)")
    hero_slideshow_speed = models.PositiveIntegerField(default=5000, help_text="Slideshow transition speed in milliseconds", verbose_name="Slideshow Speed (ms)")
    
    # NEW: Hero Background Image
    hero_background_image = models.ImageField(upload_to='hero/background/', blank=True, null=True, verbose_name="Hero Background Image")
    
    # Hero Slider Images (for backward compatibility)
    hero_image_1 = models.ImageField(upload_to='site/hero/', blank=True, null=True, verbose_name="Hero Image 1")
    hero_image_2 = models.ImageField(upload_to='site/hero/', blank=True, null=True, verbose_name="Hero Image 2")
    hero_image_3 = models.ImageField(upload_to='site/hero/', blank=True, null=True, verbose_name="Hero Image 3")
    
    # Color Scheme
    primary_color = models.CharField(max_length=20, default='#6366f1', verbose_name="Primary Color")
    secondary_color = models.CharField(max_length=20, default='#3b82f6', verbose_name="Secondary Color")
    accent_color = models.CharField(max_length=20, default='#f59e0b', verbose_name="Accent Color")
    footer_bg_color = models.CharField(max_length=20, default='#111827', verbose_name="Footer Background Color")
    footer_text_color = models.CharField(max_length=20, default='#9ca3af', verbose_name="Footer Text Color")
    
    # NEW: Footer Settings
    footer_height = models.CharField(
        max_length=20,
        default='auto',
        help_text="Footer height (auto or pixels like 300px)",
        verbose_name="Footer Height"
    )
    footer_layout = models.CharField(
        max_length=20,
        choices=[
            ('4cols', '4 Columns (Full width)'),
            ('3cols', '3 Columns (Compact)'),
            ('centered', 'Centered (Single column)')
        ],
        default='4cols',
        verbose_name="Footer Layout"
    )
    footer_link_color = models.CharField(
        max_length=20,
        default='#e5e7eb',
        verbose_name="Footer Link Color"
    )
    
    # Social Media Links
    facebook_url = models.URLField(blank=True, verbose_name="Facebook URL")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram URL")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter URL")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube URL")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    
    # Contact Info
    contact_email = models.EmailField(default='support@jadidtechnology.com', verbose_name="Contact Email")
    contact_phone = models.CharField(max_length=20, default='+880123456789', verbose_name="Contact Phone")
    contact_address = models.TextField(blank=True, verbose_name="Office Address")
    
    # Footer Settings
    footer_copyright = models.CharField(max_length=200, default='© 2024 Jadid Technology. All rights reserved.', verbose_name="Copyright Text")
    show_newsletter = models.BooleanField(default=True, verbose_name="Show Newsletter Section")
    
    # SEO Settings
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Default Meta Title")
    meta_description = models.TextField(blank=True, verbose_name="Default Meta Description")
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name="Default Meta Keywords")
    
    # Maintenance Mode
    maintenance_mode = models.BooleanField(default=False, verbose_name="Maintenance Mode")
    maintenance_message = models.TextField(default='Site is under maintenance. Please check back soon!', verbose_name="Maintenance Message")
    
    # Analytics & Tracking
    google_analytics_id = models.CharField(max_length=50, blank=True, verbose_name="Google Analytics ID")
    facebook_pixel_id = models.CharField(max_length=50, blank=True, verbose_name="Facebook Pixel ID")
    custom_css = models.TextField(blank=True, verbose_name="Custom CSS")
    custom_js = models.TextField(blank=True, verbose_name="Custom JavaScript")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return self.site_name
    
    def get_hero_images(self):
        """Get list of non-empty hero images"""
        images = []
        for i in range(1, 4):
            img = getattr(self, f'hero_image_{i}')
            if img:
                images.append(img)
        return images
    
    def get_hero_slides(self):
        """Get active hero slides"""
        return HeroSlide.objects.filter(is_active=True)
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            return  # Skip creating duplicate
        super().save(*args, **kwargs)
        
        # ==================== CATEGORY MODELS ====================

class Category(models.Model):
    """
    Main product categories (e.g., Phone, Laptop, Tablet)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True, default='fas fa-folder')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        cache.delete('navbar_categories')
    
    @property
    def active_subcategories(self):
        return self.subcategories.filter(is_active=True)
    
    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class SubCategory(models.Model):
    """
    Sub-categories under main categories (e.g., Apple, Samsung, Oppo under Phone)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True, default='fas fa-folder')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Sub Categories"
        ordering = ['order', 'name']
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.category.name} > {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Ensure slug is unique
        original_slug = self.slug
        counter = 1
        while SubCategory.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)
        
        # Clear cache
        cache.delete('navbar_categories')
    
    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


# ==================== BRAND MODEL ====================

class Brand(models.Model):
    TIER_CHOICES = [
        ('premium', 'Premium'),
        ('standard', 'Standard'),
        ('budget', 'Budget'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    #description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brands/logos/', blank=True, null=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='standard')
    website = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    show_in_brands = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            
            while Brand.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('brand_products', args=[self.slug])
    
    def get_tier_display(self):
        return dict(self.TIER_CHOICES).get(self.tier, self.tier)

class Product(models.Model):
    # ==================== RELATIONS ====================
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    # ==================== BASIC INFO ====================
    name = models.CharField(
        max_length=200,
        verbose_name="Product Name"
    )
    
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name="URL Slug"
    )
    
    sku = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Stock Keeping Unit",
        help_text="Unique product identifier"
    )
    
    # ==================== PRICING ====================
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Selling Price",
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    compare_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Compare/Original Price",
        help_text="Original price to show discount"
    )
    
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Cost Price",
        help_text="Purchase price for profit calculation"
    )
    
    # ==================== SPECIFICATIONS ====================
    # Performance
    ram = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="RAM"
    )
    
    storage = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Storage"
    )
    
    processor = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Processor"
    )
    
    operating_system = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Operating System"
    )
    
    # Display
    display_size = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Display Size"
    )
    
    display_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Display Type",
        help_text="e.g., AMOLED, IPS LCD"
    )
    
    refresh_rate = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Refresh Rate",
        help_text="e.g., 120Hz, 90Hz"
    )
    
    resolution = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Resolution",
        help_text="e.g., 2400x1080 pixels"
    )
    
    # Camera
    camera = models.TextField(
        blank=True,
        verbose_name="Camera Setup",
        help_text="e.g., 50MP + 12MP + 12MP"
    )
    
    front_camera = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Front Camera"
    )
    
    video_recording = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Video Recording"
    )
    
    # Battery & Connectivity
    battery_capacity = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Battery Capacity"
    )
    
    charging_speed = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Charging Speed"
    )
    
    network = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Network",
        help_text="e.g., 5G, 4G LTE"
    )
    
    sim_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="SIM Type"
    )
    
    # Dimensions & Build
    dimensions = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Dimensions"
    )
    
    weight = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Weight"
    )
    
    build_material = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Build Material"
    )
    
    colors = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Available Colors",
        help_text="Comma separated list of colors"
    )
    
    # ==================== DESCRIPTIONS ====================
    description = models.TextField(
        blank=True,
        verbose_name="Product Description"
    )
    
    features = models.TextField(
        blank=True,
        verbose_name="Key Features",
        help_text="One feature per line"
    )
    
    whats_in_box = models.TextField(
        blank=True,
        verbose_name="What's in the Box",
        help_text="List of items included"
    )
    
    # ==================== MEDIA ====================
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name="Main Product Image"
    )
    
    # ==================== INVENTORY ====================
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock Quantity"
    )
    
    low_stock_threshold = models.PositiveIntegerField(
        default=10,
        verbose_name="Low Stock Threshold"
    )
    
    allow_backorder = models.BooleanField(
        default=False,
        verbose_name="Allow Backorder"
    )
    
    # ==================== STATUS ====================
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Product is visible to customers"
    )
    
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Featured",
        help_text="Show in featured products section"
    )
    
    is_new = models.BooleanField(
        default=False,
        verbose_name="New Arrival",
        help_text="Mark as new product"
    )
    
    is_best_seller = models.BooleanField(
        default=False,
        verbose_name="Best Seller"
    )
    
    # ==================== WARRANTY & SUPPORT ====================
    warranty = models.CharField(
        max_length=100,
        blank=True,
        default="1 Year",
        verbose_name="Warranty Period"
    )
    
    warranty_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Warranty Type",
        help_text="e.g., Manufacturer, Seller"
    )
    
    return_policy = models.CharField(
        max_length=200,
        blank=True,
        default="7 Days Return Policy",
        verbose_name="Return Policy"
    )
    
    # ==================== SEO & METADATA ====================
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Meta Title"
    )
    
    meta_description = models.TextField(
        blank=True,
        verbose_name="Meta Description"
    )
    
    meta_keywords = models.TextField(
        blank=True,
        verbose_name="Meta Keywords",
        help_text="Comma separated keywords"
    )
    
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Product Tags",
        help_text="Comma separated tags for filtering"
    )
    
    # ==================== RATING & REVIEWS ====================
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name="Average Rating"
    )
    
    total_reviews = models.PositiveIntegerField(
        default=0,
        verbose_name="Total Reviews"
    )
    
    total_sold = models.PositiveIntegerField(
        default=0,
        verbose_name="Total Sold"
    )
    
    # ==================== TIMESTAMPS ====================
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Published At"
    )

    # ==================== METHODS ====================
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            
            while Product.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        # Auto-generate SKU if not provided
        if not self.sku:
            # Generate SKU from brand, category, and timestamp
            brand_code = self.brand.name[:3].upper() if self.brand else "PRO"
            category_code = self.category.name[:3].upper() if self.category else "GEN"
            timestamp = str(int(time.time()))[-6:]  # ✅ time module ব্যবহার
            sku_value = f"{brand_code}-{category_code}-{timestamp}"
            
            # Ensure SKU is unique
            counter = 1
            while Product.objects.filter(sku=sku_value).exclude(id=self.id).exists():
                sku_value = f"{brand_code}-{category_code}-{timestamp}-{counter}"
                counter += 1
            
            self.sku = sku_value
        
        # Set published_at if product is being activated
        if self.is_active and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.brand.name if self.brand else 'No Brand'}"
    
    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.compare_price and self.compare_price > self.price:
            discount = ((self.compare_price - self.price) / self.compare_price) * 100
            return round(discount, 1)
        return 0
    
    def get_discount_amount(self):
        """Calculate discount amount"""
        if self.compare_price and self.compare_price > self.price:
            return self.compare_price - self.price
        return 0
    
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0
    
    def is_low_stock(self):
        """Check if product is low in stock"""
        return 0 < self.stock_quantity <= self.low_stock_threshold
    
    def get_stock_status(self):
        """Get stock status text"""
        if self.stock_quantity == 0:
            return "Out of Stock"
        elif self.stock_quantity <= self.low_stock_threshold:
            return "Low Stock"
        else:
            return "In Stock"
    
    def get_colors_list(self):
        """Convert colors string to list"""
        if self.colors:
            return [color.strip() for color in self.colors.split(',')]
        return []
    
    def get_features_list(self):
        """Convert features text to list"""
        if self.features:
            return [feature.strip() for feature in self.features.split('\n') if feature.strip()]
        return []
    
    def get_tags_list(self):
        """Convert tags string to list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_absolute_url(self):
        """Get absolute URL for product"""
        from django.urls import reverse
        try:
            return reverse('product_detail', kwargs={'slug': self.slug})
        except:
            return '#'
    
    @property
    def display_price(self):
        """Get display price with currency symbol"""
        return f"৳{self.price:,}"
    
    @property
    def display_compare_price(self):
        """Get display compare price with currency symbol"""
        if self.compare_price:
            return f"৳{self.compare_price:,}"
        return None
    
    @property
    def thumbnail_url(self):
        """Get thumbnail URL"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return "/static/images/product-placeholder.jpg"

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='gallery',  # gallery হিসেবে রিলেটেড নেম
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='products/gallery/')
    is_main = models.BooleanField(default=False)  # প্রধান ইমেজ চিহ্নিত করতে
    is_active = models.BooleanField(default=True)  # ← এই লাইনটি যোগ করুন
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_main', '-created_at']  # প্রধান ইমেজ আগে দেখাবে

    def __str__(self):
        return f"Image for {self.product.name}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='customers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHODS = [
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
    ]

    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='pending'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    shipping_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    customer_note = models.TextField(blank=True, null=True)

    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.digits, k=6))
        return f"ORD-{timestamp}-{random_str}"

    def update_totals(self):
        items = self.items.all()
        subtotal = sum(item.total_price for item in items)
        self.subtotal = subtotal
        self.total_amount = subtotal + self.shipping_charge - self.discount
        self.save(update_fields=['subtotal', 'total_amount'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_totals()

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ({self.user.username})"
    
    @property
    def total_items(self):
        total = self.items.aggregate(total=models.Sum('quantity'))['total']
        return total or 0
    
    @property
    def total_price(self):
        total = 0
        for item in self.items.all():
            total += item.subtotal()
        return total
    
    @property
    def is_empty(self):
        return not self.items.exists()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def subtotal(self):
        return self.product.price * self.quantity


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']
        verbose_name = "Wishlist"
        verbose_name_plural = "Wishlists"
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# =============== SIGNALS ===============

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
        Customer.objects.create(user=instance)


@receiver(post_save, sender=CartItem)
def update_cart_on_item_change(sender, instance, **kwargs):
    if instance.cart:
        instance.cart.updated_at = timezone.now()
        instance.cart.save(update_fields=['updated_at'])


@receiver(post_delete, sender=CartItem)
def update_cart_on_item_delete(sender, instance, **kwargs):
    if instance.cart:
        instance.cart.updated_at = timezone.now()
        instance.cart.save(update_fields=['updated_at'])


@receiver(post_save, sender=OrderItem)
def update_product_stock_on_order(sender, instance, created, **kwargs):
    """Update product stock when order item is created"""
    if created and instance.product:
        product = instance.product
        if product.stock_quantity >= instance.quantity:
            product.stock_quantity -= instance.quantity
            product.total_sold += instance.quantity
            product.save()


@receiver(post_delete, sender=OrderItem)
def restore_product_stock_on_delete(sender, instance, **kwargs):
    """Restore product stock when order item is deleted"""
    if instance.product:
        product = instance.product
        product.stock_quantity += instance.quantity
        product.total_sold = max(0, product.total_sold - instance.quantity)
        product.save()

  

