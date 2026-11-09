from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class Customer(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    groups = models.ManyToManyField(Group, related_name='customer_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='customer_permissions')
    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.email}, {self.phone}"

class Havaalanlari(models.Model):
    sehir = models.CharField(max_length=100)  # Added max_length for CharField
    code = models.CharField(max_length=10, unique=True)  # Added code field
    
    def __str__(self):
        return f"{self.code} - {self.sehir}"

class Ucuslar(models.Model):
    kalkis_havaalani = models.ForeignKey(Havaalanlari, on_delete=models.CASCADE, related_name='kalkis_havaalanlari')
    varis_havaalani = models.ForeignKey(Havaalanlari, on_delete=models.CASCADE, related_name='varis_havaalanlari')
    kalkis_zamani = models.DateTimeField()
    inis_zamani = models.DateTimeField()  # Updated field name
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.kalkis_havaalani}, {self.varis_havaalani}, {self.kalkis_zamani}, {self.inis_zamani}, {self.fiyat}"