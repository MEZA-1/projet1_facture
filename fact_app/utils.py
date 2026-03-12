from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)

from fact_app.models import Invoice


def pagination(request, invoices):

    
        #difault page 

        default_page = 1

        page = request.GET.get('page', default_page)

        #page item

        item_per_page = 10

        paginator = Paginator(invoices,item_per_page)

        try:
            items_page = paginator.page(page)

        except PageNotAnInteger:

            items_page = paginator.page(default_page)
            
        except EmptyPage:

            items_page = paginator.page(paginator.num_pages)

        return items_page

def get_invoice(pk):
     """ get invoice function"""
     obj = Invoice.objects.get(pk=pk)

     articles = obj.articles.all()

     context = {
            'obj': obj,
            'articles': articles
        }
     return context