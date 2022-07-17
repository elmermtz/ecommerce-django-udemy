from itertools import product
from django.shortcuts import render, redirect, get_object_or_404
from carts.models import Cart, CartItem
from store.models import Product
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

# _______Funcion para crear carrito con su id_______
def _cart_id(request):
    # el carrito va a ser igual a la session del request
    cart = request.session.session_key
    # Si no existe el carrito se creara uno con la session
    if not cart:
        cart = request.session.create()
    # Si existe ya existe entonces la funcion la retornara
    return cart


# ______Funcion para anadir o ACTUALIZAR productos al carrito_______
def add_cart(request, product_id):
    # Inicializa var product siendo product_id del request igual a la id
    product = Product.objects.get(id=product_id)

    # Se asegura primero exista carro cuya id sea igual al resultado
    # de la funcion _cart_id
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request),
        )
    cart.save()

    # El item sera llamado cart_item donde product debe ser igual ala 
    # variable producto del principio y cart(carro) a la var cart
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        # Cada vez se oprima el boton se sumara un item mas
        cart_item.quantity +=1
        # Se guarda
        cart_item.save()

    # Si no existiera el item entonces se creara aqui
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        cart_item.save()

    return redirect('cart')

# ______Funcion para disminuir item del carrito a traves del boton_____
def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity>1:
        cart_item.quantity -= 1
        cart_item.save()

    else:
        cart_item.delete()

    return redirect('cart')

# ____Funcion para borrar un item del carrito____
def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


#  ____Funcion para consultar lo que hay en el carrito de compras____


def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        # La var cart sera igual a la id del carrito igual al 
        # id del request
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # La var cart_items tiene los objetos almacenados en cart iguales
        # al cart de la BD
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        # Se saca el total y cantidad de objetos en var car_items anterior
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity =+ cart_item.quantity
        
        # Aqui la logica para exhibir total en el carrito
        # ejemplo del tax del 2 porciento
        tax = (2*total)/100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass #solo ignora la excepcion

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }



    return render(request, 'store/cart.html', context)