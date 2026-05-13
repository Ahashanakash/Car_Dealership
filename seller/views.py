from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from cars.models import Car, CarVideo
from cars.ml.save_price_prediction import save_price_prediction_for_car

from .forms import CarForm, CarVideoForm
from profiles.mixins import IsSellerMixin


class SellerDashBoardView(LoginRequiredMixin, IsSellerMixin, TemplateView):
    template_name = 'seller_dashboard.html'


def safely_save_price_prediction(car):
    """
    Runs AI/XGBoost price prediction after car save/update.
    This keeps car posting working even if prediction fails.
    """
    try:
        save_price_prediction_for_car(car)
    except Exception as error:
        print(f"Price prediction failed for car ID {car.id}: {error}")


# HTMX: Add Car
@login_required
def add_car_htmx(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)

        if form.is_valid():
            car = form.save(commit=False)
            car.seller = request.user
            car.save()

            # AI price prediction after new car is saved
            safely_save_price_prediction(car)

            return redirect('seller:your-cars')

    else:
        form = CarForm()

    return render(request, 'partials/add_car_form.html', {
        'form': form
    })


# HTMX: Your Cars list
@login_required
def your_cars_htmx(request):
    cars = Car.objects.filter(
        seller=request.user
    ).select_related(
        'brand',
        'price_prediction'
    )

    return render(request, 'partials/your_cars_list.html', {
        'cars': cars
    })


# HTMX: Update Car
@login_required
def update_car_htmx(request, pk):
    car = get_object_or_404(Car, pk=pk, seller=request.user)

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)

        if form.is_valid():
            updated_car = form.save()

            # AI price prediction after car is updated
            safely_save_price_prediction(updated_car)

            cars = Car.objects.filter(
                seller=request.user
            ).select_related(
                'brand',
                'price_prediction'
            ).order_by('-id')

            return render(request, 'partials/your_cars_list.html', {
                'cars': cars
            })

    else:
        form = CarForm(instance=car)

    return render(request, 'partials/edit_car.html', {
        'form': form,
        'car': car
    })


# HTMX: Delete Car
@login_required
def delete_car_htmx(request, pk):
    car = get_object_or_404(Car, pk=pk, seller=request.user)
    car.delete()

    return HttpResponse('')


# HTMX: Add Video
@login_required
def add_video_htmx(request, pk):
    car = get_object_or_404(Car, pk=pk, seller=request.user)

    existing_video = CarVideo.objects.filter(model=car).first()

    if request.method == 'POST':
        form = CarVideoForm(request.POST, request.FILES, instance=existing_video)

        if form.is_valid():
            video = form.save(commit=False)
            video.model = car
            video.save()

            return render(request, 'partials/video_added.html', {
                'video': video
            })

    else:
        form = CarVideoForm(instance=existing_video)

    return render(request, 'partials/add_video_form.html', {
        'form': form,
        'car': car
    })