from django.db import models

class Product(models.Model):
    websiteName = models.CharField(max_length=100)
    redirectLink = models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    imageUrl = models.URLField()

    def __str__(self):
        return self.name