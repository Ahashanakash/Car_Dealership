class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, car):
        car_id = str(car.id)

        if car_id not in self.cart:
            self.cart[car_id] = {
                'price': str(car.price),
                'quantity': 1,
                'brand': car.brand.name,
                'model': car.car_model
            }
        else:
            self.cart[car_id]['quantity'] += 1

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, car):
        car_id = str(car.id)

        if car_id in self.cart:
            del self.cart[car_id]
            self.save()

    def update(self, car, qty):
        car_id = str(car.id)

        if car_id in self.cart:
            self.cart[car_id]['quantity'] = qty
            self.save()

    def total(self):
        return sum(
            float(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def count(self):
        return sum(item['quantity'] for item in self.cart.values())