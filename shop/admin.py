from django.contrib import admin

from shop import models


class OrderProducts(admin.TabularInline):
    model = models.OrderProducts

    def get_field_queryset(self, db, db_field, request):
        if db_field.name == 'product':
            return models.Product.objects.select_related('subcategory')


class Articles(admin.TabularInline):
    model = models.Article.products.through
    verbose_name = 'связанная статья'
    verbose_name_plural = 'связанные статьи'


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (Articles,)
    prepopulated_fields = {'slug': ['title']}


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


@admin.register(models.Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


@admin.register(models.Feedback)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderProducts
    ]
