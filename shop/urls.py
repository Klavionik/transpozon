from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('signup/',
         views.SignUp.as_view(),
         name='signup'),
    path('login/',
         views.Login.as_view(template_name='shop/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(template_name='shop/index.html'),
         name='logout'),
    path('', views.IndexView.as_view(),
         name='index'),
    path('cart/',
         views.CartView.as_view(),
         name='cart'),
    path('cart/add/<int:product_id>/',
         views.AddProductToCart.as_view(),
         name='cart-add'),
    path('new-order/', views.NewOrder.as_view(),
         name='new-order'),
    path('catalog/<slug:category>/',
         views.SubcategoryList.as_view(),
         name='category'),
    path('catalog/<slug:category>/<slug:subcategory>/',
         views.ProductList.as_view(),
         name='subcategory'),
    path('catalog/<slug:category>/<slug:subcategory>/<slug:product>/',
         views.ProductView.as_view(),
         name='product'),
    path('article/<slug:title>',
         views.ArticleView.as_view(),
         name='article')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
