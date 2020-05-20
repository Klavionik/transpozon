from .models import Product


class Item:

    def __init__(self, product, qty):
        self.id = product.id
        self.title = product.title
        self.description = product.description
        self.price = product.price
        self.image = product.image.url
        self.url = product.get_absolute_url()
        self.qty = qty

    @property
    def total_price(self):
        return self.price * self.qty

    def __str__(self):
        return f'{self.title} {self.qty} {self.total_price}'


class Cart:

    def __init__(self, session_cart):
        self.raw_cart = session_cart
        self.items = []
        self.item_qty = 0
        self.subtotal = 0

        self.initialize_cart()

    def initialize_cart(self):
        cart_products = Product.objects.\
            filter(id__in=self.raw_cart.keys()).\
            prefetch_related('category', 'subcategory')

        for product in cart_products:
            qty = self.raw_cart[str(product.id)]
            item = Item(product, qty)
            self.item_qty += qty
            self.subtotal += item.total_price
            self.items.append(item)

    def __str__(self):
        return {self.raw_cart}
