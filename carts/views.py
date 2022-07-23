from itertools import product
from django.shortcuts import render, redirect, get_object_or_404
from carts.models import Cart, CartItem
from store.models import Product, Variation
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
    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass




    # Se asegura primero exista carro cuya id sea igual al resultado
    # de la funcion _cart_id, si no entonces CREARA EL CARRITO
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request),
        )
    cart.save()

    # SE CONSTATA QUE EXISTE UN ITEM PARA ANADIR AL CARRO
    # DE NO EXISTIR ENTONCES LO CREAREMOS

    # variable para saber si el ITEM (cart_item) existe o no
    is_cart_item_exist = CartItem.objects.filter(product=product, cart=cart).exists
    if is_cart_item_exist:
        # ITEM(cart_item) entonces sera igual al item que ya esta en la BD
        cart_item = CartItem.objects.filter(product=product, cart=cart)


        #Procederemos a comparar si las variaciones son las mismas 
        
        # Creamos las listas vacias
        ex_var_list = []
        id = []

        # Para el ITEM(cart_item)
        for item in cart_item:
            # Almacene todas las variaciones en var existing_variation
            existing_variation = item.variations.all()
            #Anadalas a la lista ex_var_list creada arriba
            ex_var_list.append(list(existing_variation))
            # Anada el id del item a la lista id creada arriba
            id.append(item.id)

        # Si las variaciones que me esta enviando el cliente esta en BD(ex_var_list)
        if product_variation in ex_var_list:
            # retorna el numero INDICE de esas variaciones 
            index = ex_var_list.index(product_variation)
            # Retorne el item_id de ese INDICE
            item_id = id[index]
            # Ahora el item es igual al producto que tiene como ID item_id
            item = CartItem.objects.get(product=product, id=item_id)
            # Suma uno a ese item.quantity
            item.quantity += 1

            item.save()

         # Si las variaciones que me esta enviando el cliente NO ESTAN en BD(ex_var_list)
        else:
            # Se crea el ITEM con las especificaciones pertinente
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            # Si existen variations en la lista(product_variation) se debe limpiar
            if len(product_variation) > 0:
                item.variations.clear()
            # Anada las variaciones a la lista
                item.variations.add(*product_variation)
            item.save()
            
    # Si no existiera el ITEM entonces se creara aqui con las especificaciones siguientes
    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        #si existieran variations en la lista se debe limpiar
        if len(product_variation) > 0 :
            cart_item.variations.clear()
        # Se anaden las variaciones a la lista
            cart_item.variations.add(*product_variation)

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