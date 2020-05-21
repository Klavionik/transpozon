from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, TemplateView, ListView
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from .cart import Cart
from .forms import SignupForm, FeedbackForm
from .models import Product, Category, Subcategory, Order, Article


class SignUp(CreateView):
    template_name = "shop/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        message = 'Успешная регистрация! Теперь вы можете войти.'
        messages.success(self.request, message)
        return super().form_valid(form)


class Login(LoginView):

    def get_context_data(self, **kwargs):
        if self.request.session.get('from_neworder'):
            message = 'Для оформления заказа необходимо войти в личный кабинет.'
            messages.info(self.request, message)
            del self.request.session['from_neworder']

        return super().get_context_data(**kwargs)


class HomeView(ListView):
    template_name = 'shop/home.html'
    model = Article
    context_object_name = 'articles'
    ordering = ['-date_posted']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset. \
            prefetch_related('products', 'products__category', 'products__subcategory',)[:6]


class ArticleView(DetailView):
    context_object_name = 'article'
    model = Article
    slug_url_kwarg = 'title'
    ordering = ['-date_posted']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('products__category', 'products__subcategory')


class SubcategoryList(ListView):
    model = Subcategory

    def dispatch(self, request, *args, **kwargs):
        self.slug = self.kwargs.get('category')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        category = Category.objects.filter(slug=self.slug).first()
        self.category_title = category.title
        queryset = super().get_queryset()
        return queryset.filter(category=category).prefetch_related('category')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['category_title'] = self.category_title
        return context


class ProductList(ListView):
    model = Product
    paginate_by = 4
    ordering = ['-title']

    def dispatch(self, request, *args, **kwargs):
        self.slug = self.kwargs.get('subcategory')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        subcategory = Subcategory.objects.filter(slug=self.slug).first()
        self.subcategory_title = subcategory.title
        queryset = super().get_queryset()
        return queryset.filter(subcategory=subcategory).prefetch_related('subcategory', 'category')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['subcategory_title'] = self.subcategory_title
        return context


class ProductDetail(DetailView):
    model = Product
    slug_url_kwarg = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FeedbackForm(initial={'product': self.object})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('reviews')


class ProductFeedback(SingleObjectMixin, FormView):
    template_name = 'shop/product_detail.html'
    model = Product
    form_class = FeedbackForm
    slug_url_kwarg = 'product'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class ProductView(View):

    def get(self, request, *args, **kwargs):
        view = ProductDetail.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductFeedback.as_view()
        return view(request, *args, **kwargs)


class AddProductToCart(View):

    def dispatch(self, request, *args, **kwargs):
        self.pk = str(self.kwargs.get('product_id'))
        if not request.is_ajax():
            return HttpResponse(status=405)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        success_message = 'Добавлено!'
        failure_message = 'Ошибка, попробуйте еще раз.'

        if 'cart' not in request.session:
            request.session['cart'] = {}

        if self.product_exists():
            self.update_cart()
            return JsonResponse({'message': success_message})
        else:
            return JsonResponse({'message': failure_message})

    def product_exists(self):
        return Product.objects.filter(id__exact=self.pk).exists()

    def update_cart(self):
        product_qty = self.request.session['cart'].get(self.pk, 0)
        self.request.session['cart'][self.pk] = product_qty + 1
        self.request.session.modified = True


class CartView(TemplateView):
    template_name = 'shop/cart.html'

    def get(self, request, *args, **kwargs):
        session_cart = request.session.get('cart')

        if session_cart and request.GET.get('clear'):
            return self.clean_cart()

        if session_cart:
            context = self.get_cart(session_cart)
        else:
            context = self.get_context_data()

        return self.render_to_response(context)

    def clean_cart(self):
        del self.request.session['cart']
        return redirect('cart')

    def get_cart(self, session_cart):
        cart = Cart(session_cart)
        return self.get_context_data(cart=cart)


class NewOrder(LoginRequiredMixin, TemplateView):
    template_name = 'shop/order_success.html'
    login_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        if cart := self.request.session.get('cart'):
            order_id = Order.checkout(request.user, cart)
            del request.session['cart']
            context = self.get_context_data(order_id=order_id)
            return self.render_to_response(context)
        else:
            redirect('cart')

    def handle_no_permission(self):
        self.request.session['from_neworder'] = True
        return super().handle_no_permission()
