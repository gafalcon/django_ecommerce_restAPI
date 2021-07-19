from django.contrib import admin

from .models import Category, Product, Review

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)
# Register your models here.
