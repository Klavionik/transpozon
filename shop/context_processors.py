from .models import Category


def navbar(httprequest):
    categories = Category.objects.order_by('-id').prefetch_related('subcategories')
    return {'navbar_categories': categories}
