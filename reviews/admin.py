from django.contrib import admin
from .models import Review
# Register your models here.
# -----------------------------
# Comments Admin
# -----------------------------
# @admin.register(Comment)
# class CommentsAdmin(admin.ModelAdmin):
#     list_display = ('car', 'user', 'short_body', 'created_on')
#     search_fields = ('car__car_model', 'user__username', 'body')
#     list_filter = ('created_on',)
    
#     def short_body(self, obj):
#         return obj.body[:50] + ("..." if len(obj.body) > 50 else "")
#     short_body.short_description = "Comment"

# -----------------------------
# Reviews Admin
# -----------------------------
@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('car__car_model', 'user__username', 'body')