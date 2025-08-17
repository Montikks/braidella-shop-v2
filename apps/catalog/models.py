from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150, unique=True, allow_unicode=False)

    class Meta:
        ordering = ["name"]
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorie"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "kategorie"
            s = base
            i = 2
            while Category.objects.filter(slug=s).exclude(pk=self.pk).exists():
                s = f"{base}-{i}"
                i += 1
            self.slug = s
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_list_by_category", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, allow_unicode=False, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cena s DPH v CZK")
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "produkt"
            s = base
            i = 2
            while Product.objects.filter(slug=s).exclude(pk=self.pk).exists():
                s = f"{base}-{i}"
                i += 1
            self.slug = s
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])
