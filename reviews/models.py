from django.db import models
from profiles.models import User
from cars.models import Car
from .constants import STAR_CHOICES

# Create your models here.
# class Comment(models.Model):
#     car = models.ForeignKey(Car,on_delete=models.CASCADE,related_name='comments')
#     user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comments')
#     body = models.TextField()
#     created_on = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Comment by {self.user.username} on {self.car}"
    

class Review(models.Model):
    car = models.ForeignKey(
        Car, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    rating = models.IntegerField(choices=STAR_CHOICES)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('car', 'user')  # One review per user per car
        ordering = ['-created_at']         # Newest first

    def __str__(self):
        return f"{self.user.username} - {self.car.car_model} ({self.rating})"