from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100, unique=True)  # Unique service names to avoid duplication
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(help_text="Estimated duration in minutes")
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.duration_minutes} min"

class Product(models.Model):
    """
    Inventory Management [PDF Module 1.4]
    Track usage of saloon products (Shampoos, Creams).
    """
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0, db_index=True)  # Indexed for quick lookup of low-stock items
    low_stock_threshold = models.PositiveIntegerField(default=5, help_text="Alert when stock dips below this")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost per unit")
    
    
    class Meta:
        unique_together = ('name', 'brand')  # Prevent duplicate products: Same name and brand cannot exist twice

    def __str__(self):
        return f"{self.name} ({self.stock_quantity} left)"