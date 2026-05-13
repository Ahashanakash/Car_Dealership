from django.contrib import admin
from .models import Profile,Purchase, User
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "phone",
        "is_customer",
        "is_seller",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_customer",
        "is_seller",
        "is_staff",
        "is_active",
    )

    ordering = ("-created_at",)

    search_fields = ("email", "username", "phone")

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone")}),
        ("Verification", {"fields": ("is_phone_verified",)}),
        (
            "Roles",
            {"fields": ("is_customer", "is_seller")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_customer",
                    "is_seller",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
admin.site.register(User, CustomUserAdmin)



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'date_of_birth')
    search_fields = ('user__username', 'address')
    # list_filter = ('is_phone_verified',)
    
    def address_preview(self, obj):
        return obj.address[:50] + ("..." if len(obj.address) > 50 else "")
    address_preview.short_description = "Address"

# -----------------------------
# Purchase Admin
# -----------------------------

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('car', 'buyer', 'price_paid',
                    'purchased_at', 'purchased_type')
    list_filter = ('purchased_at', 'purchased_type')
    search_fields = ('car__car_model', 'buyer__username')