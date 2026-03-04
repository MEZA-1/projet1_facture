from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from .models import *
from django.contrib import messages

# Create your views here.

class HomeView(View):
    """Main view"""

    template_name = "index.html"

  

    def get(self, request, *args, **kwags):
        invoices = Invoice.objects.select_related("customer", "save_by").all()
        context = {"invoices": invoices}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwags):
        # Handle POST request if needed, then redirect to avoid resubmission on refresh.
        return redirect("home")


class AddCustomerView(View):
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
