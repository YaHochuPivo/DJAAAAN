from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="Название категории")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Слаг категории")

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('firstproject:product_list_by_category', args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=200, db_index=True, verbose_name="Название товара")
    slug = models.SlugField(max_length=200, db_index=True, verbose_name="Слаг товара")
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Изображение")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    available = models.BooleanField(default=True, verbose_name="В наличии")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('firstproject:product_detail', args=[self.id, self.slug])

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name="Пользователь")
    address_line1 = models.CharField(max_length=255, verbose_name="Адресная строка 1")
    address_line2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адресная строка 2")
    city = models.CharField(max_length=100, verbose_name="Город")
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name="Штат/Провинция")
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    country = models.CharField(max_length=100, verbose_name="Страна")
    is_shipping = models.BooleanField(default=True, verbose_name="Адрес доставки")
    is_billing = models.BooleanField(default=False, verbose_name="Платежный адрес")

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    def __str__(self):
        return f'{self.address_line1}, {self.city}'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name="Пользователь")
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='shipping_orders', verbose_name="Адрес доставки")
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='billing_orders', verbose_name="Платежный адрес")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    status = models.CharField(max_length=50, default='Pending', verbose_name="Статус")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Order {self.id}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name="Товар")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.IntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.id}'

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, primary_key=True, verbose_name="Заказ")
    transaction_id = models.CharField(max_length=255, unique=True, verbose_name="ID транзакции")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    currency = models.CharField(max_length=10, default='RUB', verbose_name="Валюта")
    payment_method = models.CharField(max_length=50, verbose_name="Метод оплаты")
    status = models.CharField(max_length=50, default='Pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f'Payment for Order {self.order.id}'

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Пользователь")
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Рейтинг")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        unique_together = ('product', 'user')
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-created_at',)

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Код купона")
    discount_type = models.CharField(max_length=20, choices=[('percentage', 'Процент'), ('fixed_amount', 'Фиксированная сумма')], verbose_name="Тип скидки")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Размер скидки")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Минимальная сумма заказа")
    valid_from = models.DateTimeField(verbose_name="Действует с")
    valid_to = models.DateTimeField(verbose_name="Действует до")
    active = models.BooleanField(default=True, verbose_name="Активен")
    usage_limit = models.IntegerField(blank=True, null=True, verbose_name="Лимит использования")

    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = 'Купоны'

    def __str__(self):
        return self.code

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = 'Список желаний'
        verbose_name_plural = 'Списки желаний'

    def __str__(self):
        return f'Wishlist of {self.user.username}'

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items', verbose_name="Список желаний")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items', verbose_name="Товар")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        unique_together = ('wishlist', 'product')
        verbose_name = 'Элемент списка желаний'
        verbose_name_plural = 'Элементы списка желаний'

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s wishlist"

class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название поставщика")
    contact_person = models.CharField(max_length=255, blank=True, null=True, verbose_name="Контактное лицо")
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телефон")

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True, verbose_name="Товар")
    stock_quantity = models.IntegerField(default=0, verbose_name="Количество на складе")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name = 'Инвентарь'
        verbose_name_plural = 'Инвентарь'

    def __str__(self):
        return f'Inventory for {self.product.name}'

class ShippingMethod(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    delivery_time_estimate = models.CharField(max_length=255, blank=True, null=True, verbose_name="Оценка времени доставки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = 'Метод доставки'
        verbose_name_plural = 'Методы доставки'

    def __str__(self):
        return self.name

class Return(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, primary_key=True, verbose_name="Элемент заказа")
    return_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата возврата")
    reason = models.TextField(blank=True, verbose_name="Причина")
    status = models.CharField(max_length=50, default='Pending', verbose_name="Статус")

    class Meta:
        verbose_name = 'Возврат'
        verbose_name_plural = 'Возвраты'

    def __str__(self):
        return f'Return for Order Item {self.order_item.id}'
