from django.shortcuts import render, get_object_or_404
from .models import Review
from cars.models import Car
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required


# def review_list(request, car_id):

#     car = get_object_or_404(Car, id=car_id)

#     reviews = Review.objects.filter(car=car)

#     user_review = None
#     if request.user.is_authenticated:
#         user_review = Review.objects.filter(
#             car=car,
#             user=request.user
#         ).first()

#     return render(request, "partials/review_list.html", {
#         "car": car,
#         "reviews": reviews,
#         "user_review": user_review
#     })


# def review_modal(request, car_id):

#     car = get_object_or_404(Car, id=car_id)

#     review = None
#     if request.user.is_authenticated:
#         review = Review.objects.filter(
#             car=car,
#             user=request.user
#         ).first()

#     form = ReviewForm(instance=review)

#     return render(request, "partials/review_modal.html", {
#         "form": form,
#         "car": car,
#         "review": review
#     })

# @login_required
# def review_save(request, car_id):

#     car = get_object_or_404(Car, id=car_id)

#     review = Review.objects.filter(
#         car=car,
#         user=request.user
#     ).first()

#     form = ReviewForm(request.POST, instance=review)

#     if form.is_valid():
#         review = form.save(commit=False)
#         review.car = car
#         review.user = request.user
#         review.save()

#     reviews = Review.objects.filter(car=car)

#     user_review = Review.objects.filter(
#         car=car,
#         user=request.user
#     ).first()

#     response = render(request, "partials/review_list.html", {
#         "car": car,
#         "reviews": reviews,
#         "user_review": user_review
#     })
    
#     # Add the trigger to close the modal
#     response['HX-Trigger'] = 'close-modal' 
#     return response