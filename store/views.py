from django.shortcuts import get_object_or_404, render
from carts.models import CartItem
from carts.views import _cart_id
from .models import Product
from category.models import Category
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Create your views here.
def store(request, category_slug=None):
    categories =  None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products' : paged_products,
        'product_count' : product_count,
    }

    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    #Para evitar errores con slugs invalidos hacemos un try
    try:
        #se hace comparacion con los parametros introducidos y los de la BD
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # variable booleana para ver si existe un item en el carro
        in_cart = CartItem.objects.filter(cart__cart_id =_cart_id(request), product=single_product).exists()
    except Exception as e:

        raise e
    #se pasa en el contexto el resultado de la comparacion para pasarlo al html
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_detail.html', context)