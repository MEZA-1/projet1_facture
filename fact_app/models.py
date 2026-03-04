from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum


class Customer(models.Model):
    """
    Name: customer model definition
    """
    SEX_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Feminin'),]
    
    regexEmail = '/^[^\s@]+@[^\s@]+\.[^\s@]+$/'
    regexTelephone = '/^6\d{8}$/'
 
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
        return self.name
    
   """ def valideCustomer(){


    }"""
    
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
    total_amount = models.DecimalField(max_digits=100000, decimal_places=3, default= 0)
    last_update_date_time = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    invoice_type = models.CharField(max_length=1, choices=INVOICE_TYPE)
    comments = models.TextField(blank=True, null=True, max_length=500)
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
    def __str__(self):
        return f"{self.customer.name}-{self.invoice_type}"
    
    @property
    def get_total_amount(self):
        self.total_amount = sum(article.get_total_price for article in self.articles.all())
        return self.total_amount

    def refresh_total_amount(self, save=True):
        self.total_amount = self.articles.aggregate(total=Sum("total_price"))["total"] or 0
        if save:
            self.save(update_fields=["total_amount"])
        return self.total_amount
    

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
    quantity_in_stock = models.PositiveIntegerField(default = 50)
    quantity_seiled = models.PositiveIntegerField(default = 20)
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

class Article(models.Model):
    """
    Name: article (order item) model definition
    Each article links a product to an invoice (commande).
    author: mezatiogeril@gmail.com
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='articles')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='articles')
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

    def clean(self):
        super().clean()
        if not self.product_id:
            return

        if self.quantity <= 0:
            raise ValidationError({"quantity": "La quantite commandee doit etre superieure a 0."})

        previous_article = None
        if self.pk:
            previous_article = Article.objects.filter(pk=self.pk).select_related("product").first()

        delta_quantity = self.quantity
        if previous_article and previous_article.product_id == self.product_id:
            delta_quantity = self.quantity - previous_article.quantity

        remaining_quantity = self.product.quantity_in_stock - delta_quantity
        if remaining_quantity <= 0:
            raise ValidationError({
                "quantity": (
                    "Stock insuffisant. Le reste apres commande doit etre superieur a 0."
                )
            })

        if remaining_quantity <= self.product.quantity_seiled:
            raise ValidationError({
                "quantity": (
                    "Alerte seuil. Le reste apres commande passe sous la quantite seuil du produit."
                )
            })

    def save(self, *args, **kwargs):
        if not self.product_id:
            raise ValidationError("Aucun produit selectionne.")

        with transaction.atomic():
            previous_article = None
            if self.pk:
                previous_article = (
                    Article.objects.select_for_update()
                    .select_related("product")
                    .filter(pk=self.pk)
                    .first()
                )

            current_product = Product.objects.select_for_update().get(pk=self.product_id)

            # Keep old values in case the product changed on update.
            previous_product = previous_article.product if previous_article else None
            previous_quantity = previous_article.quantity if previous_article else 0

            if previous_product and previous_product.pk != current_product.pk:
                previous_product = Product.objects.select_for_update().get(pk=previous_product.pk)
                previous_product.quantity_in_stock += previous_quantity
                previous_product.save(update_fields=["quantity_in_stock"])
                delta_quantity = self.quantity
            elif previous_article:
                delta_quantity = self.quantity - previous_quantity
            else:
                delta_quantity = self.quantity

            remaining_quantity = current_product.quantity_in_stock - delta_quantity
            if remaining_quantity <= 0:
                raise ValidationError(
                    "Stock insuffisant. Le reste apres commande doit etre superieur a 0."
                )
            if remaining_quantity <= current_product.quantity_seiled:
                raise ValidationError(
                    "Alerte seuil. Le reste apres commande passe sous la quantite seuil du produit."
                )

            self.unit_price = current_product.unit_price
            self.total_price = self.quantity * self.unit_price

            current_product.quantity_in_stock = remaining_quantity
            current_product.save(update_fields=["quantity_in_stock"])

            super().save(*args, **kwargs)
            self.invoice.refresh_total_amount(save=True)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=self.product_id)
            product.quantity_in_stock += self.quantity
            product.save(update_fields=["quantity_in_stock"])

            invoice = self.invoice
            super().delete(*args, **kwargs)
            invoice.refresh_total_amount(save=True)
