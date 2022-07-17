from .models import Cart, CartItem
from .views import _cart_id

# ___Funcion para el icono contador de items del carrito de compras___
def counter(request):
    cart_count = 0

    try:
        # Se busca el carrito y se nombra variable cart
        cart = Cart.objects.filter(cart_id = _cart_id(request))
        # Se buscan los items del carrito arriba encontrado
        cart_items = CartItem.objects.all().filter(cart=cart[:1])

        # Suma los items encontrados
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    
    except Cart.DoesNotExist:
        cart_count = 0

    return dict(cart_count=cart_count)