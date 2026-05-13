from .models import Brand
from .cart import Cart

def cart_count(request):
    cart = Cart(request)
    return {
        "cart_count": cart.count()
    }
    
    

def brands_list(request):
    return {
        "brands": Brand.objects.all()
    }