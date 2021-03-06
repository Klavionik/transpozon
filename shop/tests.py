from django.test import TestCase
from shop.models import User, Article, Subcategory, Product, Feedback, Category, Order
from shop.views import HomeView
from shop.cart import Cart


class TestUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.email = 'test@example.com'
        cls.password = 'testpassword'

    def test_signup(self):
        signup_data = {'email': self.email, 'password1': self.password, 'password2': self.password}
        response = self.client.post('/signup/', follow=True, data=signup_data)
        user_exists = User.objects.filter(email__exact=self.email).exists()

        self.assertTrue(user_exists, "User saved in the database")
        self.assertIn(('/login/', 302), response.redirect_chain,
                      "User signed up and redirected to the login page")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        User.objects.create_user(self.email, self.password)
        login_data = {'username': self.email, 'password': self.password}
        response = self.client.post('/login/', follow=True, data=login_data)

        self.assertIn(('/', 302), response.redirect_chain,
                      "User logged in and redirected to the home page")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        User.objects.create_user(self.email, self.password)
        self.client.login(username=self.email, password=self.password)
        response = self.client.post('/logout/', follow=True)

        self.assertIn(('/', 302), response.redirect_chain,
                      "User logged out and redirected to the home page")
        self.assertEqual(response.status_code, 200)


class TestContentViews(TestCase):
    fixtures = ['fixtures.json']

    def test_home(self):
        ordering = HomeView.ordering
        home_articles = Article.objects.order_by(*ordering)[:6]
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(home_articles), list(response.context_data.get('articles', [])),
                         "Page contains the last 6 articles")

    def test_article(self):
        article = Article.objects.first()
        url = f'/article/{article.slug}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(article, response.context_data.get('article'),
                         "Page contains the article")

    def test_product_list(self):
        subcategory = Subcategory.objects.filter(slug='noutbuki').first()
        url = f'/catalog/{subcategory.category.slug}/{subcategory.slug}/'
        response = self.client.get(url)
        page_objects = response.context_data['page_obj'].object_list

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(page_objects), 4, "Page contains 4 products")

    def test_subcategories_list(self):
        category = Category.objects.first()
        subcategories = category.subcategories.all()
        url = f'/catalog/{category.slug}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(subcategories), list(response.context_data.get('object_list', [])),
                         "Page contains subcategories for given category")

    def test_product_detail(self):
        product = Product.objects.first()
        category = product.category.slug
        subcategory = product.subcategory.slug
        url = f'/catalog/{category}/{subcategory}/{product.slug}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(product, response.context_data.get('product'),
                         "Page contains the product")

    def test_product_feedback(self):
        product = Product.objects.first()
        category = product.category.slug
        subcategory = product.subcategory.slug
        feedback_data = {
            'name': "John Doe", "text": "Five stars!", 'rating': 5, 'product': product.id
        }
        url = f'/catalog/{category}/{subcategory}/{product.slug}/'
        response = self.client.post(url, data=feedback_data, follow=True)
        feedback = Feedback.objects.filter(**feedback_data).exists()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(feedback, "Feedback saved in the database")


class TestCart(TestCase):

    fixtures = ['fixtures.json']

    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.first()
        cls.session_cart = {str(cls.product.id): 1}

    def test_add_product(self):
        url = f'/cart/add/{self.product.id}/'
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get('cart'), self.session_cart,
                         "The product is in the cart")

    def test_cart(self):
        url = f'/cart/add/{self.product.id}/'
        self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = self.client.get('/cart/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart(self.session_cart), response.context_data.get('cart'))

    def test_clean_cart(self):
        session = self.client.session
        session['cart'] = self.session_cart
        session.save()
        response = self.client.get('/cart/?clear=1', follow=True)

        self.assertIn(('/cart/', 302), response.redirect_chain,
                      "Cart is cleaned, redirect back to the cart page")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.session.get('cart'))

    def test_no_auth_checkout(self):
        self.client.session['cart'] = self.session_cart
        response = self.client.post('/new-order/', follow=True)

        self.assertIn(('/login/?next=/new-order/', 302), response.redirect_chain,
                      "User not authorized, redirect to the login page")
        self.assertEqual(response.status_code, 200)

    def test_checkout(self):
        email = 'test@example.com'
        password = 'testpassword'
        User.objects.create_user(email, password)
        self.client.login(username=email, password=password)
        session = self.client.session
        session['cart'] = self.session_cart
        session.save()

        response = self.client.post('/new-order/')
        order = Order.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.id, response.context_data.get('order_id'))
