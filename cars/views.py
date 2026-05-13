from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Car, CarVideo
from reviews.models import Review
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .models import Car, Brand, CarPricePrediction
from django.db.models import Q
from .constants import FUEL_TYPE, LEATHER_INTERIOR, COLOR_CHOICES, CATEGOTY
from .ai_search import extract_ai_filters, apply_ai_filters
from .ml.save_price_prediction import save_price_prediction_for_car
from .models import CarPricePrediction
from .recommendations import get_recommended_cars
from reviews.forms import ReviewForm

# For contact seller form
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from profiles.models import User



class CarList(ListView):
    model = Car
    ordering = ['id']
    paginate_by = 9
    context_object_name = "cars"
    template_name = "cars/car_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        GET = self.request.GET

        # AI SEARCH
        ai_query = GET.get("ai_query", "").strip()
        if ai_query:
            ai_filters = extract_ai_filters(ai_query)
            queryset = apply_ai_filters(queryset, ai_filters)

        filters = {
            'brand': 'brand__id',
            'fuel_type': 'fuel_type',
            'leather_interior': 'leather_interior',
            'color': 'color',
            'cylinders': 'cylinders',
            'engine_volume': 'engine_volume',
            'category': 'category'
        }

        # Range filters
        if GET.get('min_price'):
            queryset = queryset.filter(price__gte=GET['min_price'])
        if GET.get('max_price'):
            queryset = queryset.filter(price__lte=GET['max_price'])
        if GET.get('min_year'):
            queryset = queryset.filter(prod_year__gte=GET['min_year'])
        if GET.get('max_year'):
            queryset = queryset.filter(prod_year__lte=GET['max_year'])

        # Exact match filters
        for key, field in filters.items():
            value = GET.get(key)
            if value:
                queryset = queryset.filter(**{field: value})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        context['fuel_types'] = FUEL_TYPE
        context['leathers'] = LEATHER_INTERIOR
        context['colors'] = COLOR_CHOICES
        context['category'] = CATEGOTY
        context['current_filters'] = self.request.GET
        return context


    # Handle contact seller form
    @csrf_exempt
    def contact_seller(request, pk):
        if request.method == "POST":
            car = get_object_or_404(Car, pk=pk)
            seller = car.seller
            seller_email = seller.email
            buyer_email = request.POST.get("email")
            message = request.POST.get("message")
            car_brand = request.POST.get("car_brand")
            car_model = request.POST.get("car_model")
            category = request.POST.get("category")

            subject = f"Car Inquiry: {car_brand} {car_model} ({category})"
            email_message = f"Message from: {buyer_email}\n\n{message}"

            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [seller_email],
                fail_silently=False,
            )
            return HttpResponse("Message sent to seller.")
        return HttpResponse("Invalid request.", status=400)

    # Return partial for HTMX requests
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('Hx-Request'):
            return self.partial_response(context)
        return super().render_to_response(context, **response_kwargs)

    def partial_response(self, context):
        from django.template.loader import render_to_string
        html = render_to_string(
            "partials/car_list_partial.html", context, request=self.request)
        from django.http import HttpResponse
        return HttpResponse(html)


class CarDetails(DetailView):
    model = Car
    context_object_name = "car"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        car = self.object

        context["reviews"] = Review.objects.filter(car=car)

        # Car video
        try:
            context["car_video"] = car.carvideo
        except CarVideo.DoesNotExist:
            context["car_video"] = None

        # AI price prediction
        try:
            context["price_prediction"] = car.price_prediction
        except CarPricePrediction.DoesNotExist:
            context["price_prediction"] = None

        # Recommended cars
        context["recommended_cars"] = get_recommended_cars(car, limit=10)

        return context


@login_required
def toggle_like(request, pk):
    car = get_object_or_404(Car, pk=pk)

    if request.user in car.likes.all():
        car.likes.remove(request.user)
    else:
        car.likes.add(request.user)

    html = render_to_string(
        "partials/like_section.html",
        {"car": car, "user": request.user},
        request=request
    )

    return HttpResponse(html)


def review_list(request, car_id):

    car = get_object_or_404(Car, id=car_id)

    reviews = Review.objects.filter(car=car)

    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(
            car=car,
            user=request.user
        ).first()

    return render(request, "partials/review_list.html", {
        "car": car,
        "reviews": reviews,
        "user_review": user_review
    })


def review_modal(request, car_id):

    car = get_object_or_404(Car, id=car_id)

    review = None
    if request.user.is_authenticated:
        review = Review.objects.filter(
            car=car,
            user=request.user
        ).first()

    form = ReviewForm(instance=review)

    return render(request, "partials/review_modal.html", {
        "form": form,
        "car": car,
        "review": review
    })

@login_required
def review_save(request, car_id):

    car = get_object_or_404(Car, id=car_id)

    review = Review.objects.filter(
        car=car,
        user=request.user
    ).first()

    form = ReviewForm(request.POST, instance=review)

    if form.is_valid():
        review = form.save(commit=False)
        review.car = car
        review.user = request.user
        review.save()

    reviews = Review.objects.filter(car=car)

    user_review = Review.objects.filter(
        car=car,
        user=request.user
    ).first()

    return render(request, "partials/review_list.html", {
        "car": car,
        "reviews": reviews,
        "user_review": user_review,
        "close_review_modal": form.is_valid(),
    })