from django.db import models

class Category(models.Model):
    """
    Groups services (e.g., Hair Care, Skin Care, Packages).
    """
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Service(models.Model):
    """
    Individual service details (Price, Duration, etc.).
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Critical for Queue Calculation & AI
    duration_minutes = models.PositiveIntegerField(help_text="Estimated duration in minutes")
    
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)  # To hide service without deleting

    def __str__(self):
        return f"{self.name} - {self.duration_minutes} min"