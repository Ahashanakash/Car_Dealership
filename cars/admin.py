from django.contrib import admin
from .models import Brand, Car, CarVideo
from django.utils.html import format_html
from embed_video.admin import AdminVideoMixin
from .models import CarPricePrediction

admin.site.register(CarPricePrediction)

# -----------------------------
# Brand Admin
# -----------------------------


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview')
    search_fields = ('name',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="30" height="30" style="object-fit:contain;" />',
                obj.logo.url
            )
        return "-"

    logo_preview.short_description = "Logo"

# -----------------------------
# Car Admin
# -----------------------------


from django.contrib import admin
from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):

    list_display = (
        'serial_number',
        'brand',
        'car_model',
        'seller',
        'prod_year',
        'price',
        'fuel_type',
        'gear_box_type',
        'is_sold',
        'like_count',
        'dislike_count'
    )

    list_filter = (
        'brand',
        'prod_year',
        'fuel_type',
        'gear_box_type',
        'is_sold',
        'color'
    )

    search_fields = (
        'car_model',
        'brand__name',
        'seller__username',
        'serial_number'
    )

    readonly_fields = (
        'serial_number',
    )

    filter_horizontal = (
        'likes',
        'dislikes',
    )

    ordering = ('-prod_year',)

    # -------------------------
    # Custom fields
    # -------------------------

    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = "Likes"

    def dislike_count(self, obj):
        return obj.dislikes.count()
    dislike_count.short_description = "Dislikes"



# --- Use AdminVideoMixin to handle EmbedVideoField automatically ---
class CarVideoAdmin(AdminVideoMixin, admin.ModelAdmin):
    list_display = ('model', 'video')  # 'video' field will show preview automatically
    search_fields = ('model__car_model',)

admin.site.register(CarVideo, CarVideoAdmin)