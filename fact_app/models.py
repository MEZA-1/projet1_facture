from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    """
    Name: customer model definition
    """
    SEX_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Feminin'),]
 
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    age = models.CharField(max_length=12)
    city = models.CharField(max_length=100)
    zipe_code = models.CharField(max_length=18)
    created_date = models.DateTimeField(auto_now_add=True)
    save_by = models.ForeignKey(User, on_delete= models.PROTECT)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
    def __str__(self):
        return super().__str__()
    
class Invoice (models.Model):
    """
    Name: invoice model definition
    description:
    author: mezatiogeril@gmail.com
    """
    INVOICE_TYPE =[
        ('R', 'Reçu'),
        ('F', 'Facture'),
        ('P', 'Proforma_facture'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)
    invoice_date_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=100000, decimal_places=3)
    last_update_date_time = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    invoice_type = models.CharField(max_length=1, choices=INVOICE_TYPE)
    comments = models.TextField(blank=True, null=True, max_length=500)
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
    def __str__(self):
        return f"{self.customer.name}-{self.invoice_type} - {self.total_amount}"
    
    @property
    def get_total_amount(self):
        self.total_amount = sum(article.get_total_price for article in self.articles.all())
        return self.total_amount


class Article(models.Model):
    """
    Name: article (order item) model definition
    Each article links a product to an invoice (commande).
    author: mezatiogeril@gmail.com
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='articles')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, related_name='articles')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return f"{self.product.name} x{self.quantity} "
    
    @property
    def get_total_price(self):
       self.total_price = self.quantity * self.unit_price
       return self.total_price

class Product(models.Model):
    """
    Name: product model definition
    A product can appear on many invoices (commandes) through Article.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(auto_now_add=True)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name