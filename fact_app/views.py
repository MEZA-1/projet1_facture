from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import *
from django.contrib import messages
from .utils import get_invoice, pagination
import datetime
import pdfkit
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
 
 
from .decorators import * 

# Create your views here.

class HomeView(LoginRequiredSuperuserMixin,View):
    """Main view"""

    template_name = "index.html"
  

    def get(self, request, *args, **kwags):
        invoices = Invoice.objects.select_related("customer", "save_by").filter(is_annuler=False).order_by('-invoice_date_time')
        items = pagination(request, invoices)
        context = {"invoices": items}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwags):
        # Handle POST request if needed, then redirect to avoid resubmission on refresh.
        #mofify on invoice

        if request.POST.get('id_modified'):
            
            paid = request.POST.get('modified')

            try:
                obj = Invoice.objects.get(id=request.POST.get('id_modified'))
                if paid == 'true':
                    obj.paid = True
                    obj.last_update_date_time =datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                else:
                     obj.paid =False
                     obj.last_update_date_time =datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

                obj.save()
                messages.success(request," Change mode successfully. ")
            except Exception as e:
                messages.error(request, f" sorry the following error has occured {e}")

        # deleting invoice

        if request.POST.get('id_supprimer'):
            try:
                obj = Invoice.objects.get(pk=request.POST.get('id_supprimer'))
                obj.cancel()
                
                messages.success(request,'The invoice was cancelled successfully')
            except Exception as e:
                messages.error(request, f"sorry, the foolowing error has occured {e},")

        return redirect("home")

class AddCustomerView(LoginRequiredSuperuserMixin, View):
    """add new cistomer,"""
    
    template_name = "add_customer.html"
    def get(self,request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self,request, *args, **kwargs):
        data = {
        "name": request.POST.get("name"),
        "email": request.POST.get("email"),
        "phone": request.POST.get("phone"),
        "address": request.POST.get("address"),
        "sex": request.POST.get("sex"),
        "age": request.POST.get("age"),
        "city": request.POST.get("city"),
        "zipe_code": request.POST.get("zip"),
        "save_by": request.user,
        }
        try:
            created_Customer = Customer.objects.create(**data)

            if created_Customer:
                messages.success(request, "Custumer registered successfully.")
            else:
                messages.error(request, "Sorry, please try again the sent data is corrupt.")
        except Exception as e:
            messages.error(request, f"Sorry our system is detecting the following issues {e}")
       
        return redirect("home")


class AddInvoiceView(LoginRequiredSuperuserMixin, View):
    """add new invoice"""

    template_name = "add_invoice.html"

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.select_related('save_by').all().order_by("name")
        products = Product.objects.all().order_by("name")
        context = {"customers": customers, "products": products}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        customer_id = request.POST.get("customer")
        invoice_type = request.POST.get("invoice_type")
        comments = request.POST.get("comments")
        product_ids = request.POST.getlist("product")
        quantities = request.POST.getlist("qty")

        if not customer_id or not invoice_type:
            messages.error(request, "Please select a customer and an invoice type.")
            return redirect("add-invoice")

        line_items = []
        for product_id, quantity in zip(product_ids, quantities):
            if not product_id or not quantity:
                continue
            try:
                line_items.append((int(product_id), int(quantity)))
            except (TypeError, ValueError):
                messages.error(request, "Invalid product or quantity.")
                return redirect("add-invoice")

        if not line_items:
            messages.error(request, "Please add at least one product.")
            return redirect("add-invoice")

        try:
            customer = Customer.objects.get(pk=customer_id)
            with transaction.atomic():
                invoice = Invoice.objects.create(
                    customer=customer,
                    save_by=request.user,
                    invoice_type=invoice_type,
                    comments=comments,
                )
                total_amount = 0

                for product_id, quantity in line_items:

                    product = Product.objects.get(pk=product_id)
                    
                    unit_price = product.unit_price
                    
                    total_price = unit_price * quantity
                    
                    article = Article.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        )
                    total_amount += total_price
                invoice.total_amount = total_amount
                invoice.save(update_fields=["total_amount"])
                print(f"Invoice {invoice.id} created with total amount: {total_amount}")
               

            messages.success(request, "Invoice created successfully.")
        except Exception as e:
            messages.error(request, f"Unable to create invoice: {e}")
        return redirect("home")
    
class InvoiceVisualizationView(LoginRequiredSuperuserMixin, View):
    """ this view helps to visualize the invoice"""

    template_name = 'invoice.html'


    def get(self, request, *args, **kwargs): 
        
        pk = kwargs.get('pk')

        context = get_invoice(pk)

        return render(request, self.template_name, context)
    
@superuser_required
def get_imvoice_pdf(request, *args, **kwargs):
    """generate de pdf file from html file"""
    pk = kwargs.get('pk')

    context = get_invoice(pk)

    context['date']=datetime.datetime.today()

    #get html fille
    template = get_template('invoice_pdf.html')

    # render html with context variable

    html = template.render(context)
    #option of pdf format
    options = {
        'page-size': 'letter',
        'encoding': 'UTF-8',
        'no-outline': None
    }
    #generate pdf

    pdf = pdfkit.from_string(html, False, options)

    response = HttpResponse(pdf, content_type='application/pdf')

    response['Content-Disposition']= "attachement"

    return response


class AddproductView(LoginRequiredSuperuserMixin, View):
    """add new cistomer,"""
    
    template_name = "add_product.html"
    def get(self,request, *args, **kwargs):
        
        return render(request, self.template_name)
    
    def post(self,request, *args, **kwargs):
        name = (request.POST.get("name") or "").strip()
        description = request.POST.get("description")
        unit_price = request.POST.get("Unit_price")
        quantity_in_stock = request.POST.get("quantity_stock")
        quantity_seiled = request.POST.get("quantity_seiled")

        if not name:
            messages.error(request, "Product name is required.")
            return redirect("add-product")

        if Product.objects.filter(name__iexact=name).exists():
            messages.error(request, "This product already exists in the database.")
            return redirect("add-product")

        try:
            quantity_in_stock_value = int(quantity_in_stock)
            quantity_seiled_value = int(quantity_seiled)
        except (TypeError, ValueError):
            messages.error(request, "Quantity values must be numbers.")
            return redirect("add-product")

        if quantity_in_stock_value <= 0:
            messages.error(request, "Quantity in stock must be greater than 0.")
            return redirect("add-product")

        if quantity_seiled_value >= quantity_in_stock_value:
            messages.error(
                request,
                "Quantity seiled must be lower than quantity in stock.",
            )
            return redirect("add-product")

        data = {
            "name": name,
            "description": description,
            "unit_price": unit_price,
            "quantity_in_stock": quantity_in_stock_value,
            "quantity_seiled": quantity_seiled_value,
            "save_by": request.user,
        }
        
        try:
            created_Product = Product.objects.create(**data)

            if created_Product:
                messages.success(request, "Product registered successfully.")
            else:
                messages.error(request, "Sorry, please try again the sent data is corrupt.")
        except Exception as e:
            messages.error(request, f"Sorry our system is detecting the following issues {e}")
       
        return redirect("home")


class AddAdminView(LoginRequiredSuperuserMixin, View):
    """create new superuser"""

    template_name = "add_admin.html"

    def get(self, request, *args, **kwargs):

        if request.user.username != "meza":

            messages.error(request, "Only user meza can access this page.")
            
            return redirect("home")
        
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):

        if request.user.username != "meza":
            messages.error(request, "Only user meza can create admins.")
            return redirect("home")

        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("add-admin")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("add-admin")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "This username already exists.")
            return redirect("add-admin")

        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, "This email is already used.")
            return redirect("add-admin")

        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            messages.success(request, "Admin created successfully.")
        except Exception as e:
            messages.error(request, f"Unable to create admin: {e}")

        return redirect("home")


class ModifyProductStockView(LoginRequiredSuperuserMixin, View):
    """modify product stock quantity"""

    template_name = "modify_product.html"

    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by("name")
        return render(request, self.template_name, {"products": products})

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product")
        quantity_in_stock = request.POST.get("quantity_stock")

        if not product_id:
            messages.error(request, "Please select a product.")
            return redirect("modify-product")

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect("modify-product")

        try:
            quantity_in_stock_value = int(quantity_in_stock)
        except (TypeError, ValueError):
            messages.error(request, "Quantity in stock must be a number.")
            return redirect("modify-product")

        if quantity_in_stock_value <= 0:
            messages.error(request, "Quantity in stock must be greater than 0.")
            return redirect("modify-product")

        try:
            product.quantity_in_stock += quantity_in_stock_value
            product.save(update_fields=["quantity_in_stock"])
            messages.success(request, "Product stock updated successfully.")
        except Exception as e:
            messages.error(request, f"Unable to update product stock: {e}")

        return redirect("home")

class StatisticsView(LoginRequiredSuperuserMixin, View):
    """Statistics dashboard"""

    template_name = "statistics.html"

    def get(self, request, *args, **kwargs):
        customers_count = Customer.objects.count()
        paid_count = Invoice.objects.filter(is_annuler=False, paid=True).count()
        unpaid_count = Invoice.objects.filter(is_annuler=False, paid=False).count()

        top_products = (
            Article.objects.values("product__name")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")[:10]
        )

        stock_low = (
            Product.objects.filter(quantity_in_stock__lte=F("quantity_seiled"))
            .order_by("quantity_in_stock")
        )

        monthly_sales = (
            Invoice.objects.filter(is_annuler=False)
            .annotate(month=TruncMonth("invoice_date_time"))
            .values("month")
            .annotate(total=Sum("total_amount"))
            .order_by("month")
        )

        context = {
            "customers_count": customers_count,
            "paid_count": paid_count,
            "unpaid_count": unpaid_count,
            "top_products": top_products,
            "stock_low": stock_low,
            "monthly_sales": monthly_sales,
            "now": timezone.now(),
        }
        return render(request, self.template_name, context)






"""def product_info(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return JsonResponse(
        {
            "id": product.id,
            "name": product.name,
            "unit_price": float(product.unit_price),
            "quantity_in_stock": product.quantity_in_stock,
            "quantity_seiled": product.quantity_seiled,
        }
    )"""
