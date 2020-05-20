from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.shortcuts import reverse

from shop.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name='электронная почта',
    )
    date_joined = models.DateField(
        auto_now_add=True,
        verbose_name='дата регистрации',
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} {'Сотрудник' if self.is_staff else 'Клиент'}"

    class Meta:
        db_table = 'users'
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class Order(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='покупатель',
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f'№ {self.id} {self.date_created.date()} {self.customer.email}'

    @classmethod
    def checkout(cls, customer, cart):
        order = cls.objects.create(customer=customer)
        order.save()

        for product, qty in cart.items():
            OrderProducts.objects.create(
                order=order,
                product_id=product,
                quantity=qty,
            )

        return order.id

    class Meta:
        db_table = 'orders'
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderProducts(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.DO_NOTHING,
        verbose_name='заказ',
        related_name='orderproducts'
    )
    quantity = models.IntegerField(
        verbose_name='количество товара',
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.DO_NOTHING,
        verbose_name='товар',
    )

    def __str__(self):
        return f'{self.order.id} {self.order.customer}'

    class Meta:
        db_table = 'orderproducts'
        verbose_name = 'состав заказа'
        verbose_name_plural = 'состав заказа'


class Product(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name='название товара'
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name='ссылка',
    )
    description = models.TextField(
        max_length=1000,
        verbose_name='описание товара'
    )
    price = models.IntegerField(
        verbose_name='цена товара'
    )
    image = models.ImageField(
        upload_to='product_images',
        verbose_name='изображение'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        verbose_name='раздел товара',
        related_name='products',
        related_query_name='product',
    )
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.CASCADE,
        verbose_name='подраздел товара',
        related_name='products',
        related_query_name='product',
    )

    def __str__(self):
        return f'{self.title} {self.subcategory} {self.price}'

    def get_absolute_url(self):
        return reverse('product',
                       args=[self.category.slug,
                             self.subcategory.slug,
                             self.slug])

    class Meta:
        db_table = 'products'
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class Category(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='название раздела'
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name='ссылка',
    )

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('category',
                       args=[self.slug])

    class Meta:
        db_table = 'categories'
        verbose_name = 'раздел'
        verbose_name_plural = 'разделы'


class Subcategory(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='название подраздела'
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name='ссылка',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='раздел',
        related_name='subcategories',
        related_query_name="subcategory"
    )

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('subcategory',
                       args=[self.category.slug,
                             self.slug])

    class Meta:
        db_table = 'subcategories'
        verbose_name = 'подраздел'
        verbose_name_plural = 'подразделы'


class Article(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name='название статьи'
    )
    subject = models.ForeignKey(
        'Subcategory',
        on_delete=models.CASCADE,
        verbose_name='тематика',
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name='ссылка',
    )
    text = models.TextField(
        max_length=5000,
        verbose_name='текст статьи'
    )
    products = models.ManyToManyField(
        Product,
        verbose_name='товар',
        related_name='articles',
    )
    date_posted = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('article',
                       args=[self.slug])

    class Meta:
        db_table = 'articles'
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'


class Feedback(models.Model):

    RATING = (
        (5, 5),
        (4, 4),
        (3, 3),
        (2, 2),
        (1, 1),
    )

    name = models.CharField(
        max_length=30,
        verbose_name='имя'
    )
    text = models.TextField(
        max_length=500,
        verbose_name='текст отзыва'
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING,
        verbose_name='оценка',
        blank=False,
        default='unspecified',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='товар',
        related_name='reviews',
        related_query_name='review',
    )

    def __str__(self):
        return f'{self.name, self.rating}'

    class Meta:
        db_table = 'feedbacks'
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
