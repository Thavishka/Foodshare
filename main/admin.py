from django.contrib import admin
from .models import FoodItem
from .models import Profile

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'food_type', 'status', 'created_at')
    list_filter = ('status', 'food_type')
    search_fields = ('name',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')

admin.site.register(Profile, ProfileAdmin)