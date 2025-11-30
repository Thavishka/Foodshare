from django.db import models
from django.contrib.auth.models import User

# --- Profile Model ---
class Profile(models.Model):
    ROLE_CHOICES = [
        ('donor', 'Donor'),
        ('receiver', 'Receiver'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)  # ⭐ ADD THIS

    def __str__(self):
        return f"{self.user.username} ({self.role})"



# --- FoodItem Model ---
class FoodItem(models.Model):
    FOOD_TYPE_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('non-vegetarian', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('claimed', 'Claimed'),
        ('expired', 'Expired'),
    ]

    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    food_type = models.CharField(max_length=20, choices=FOOD_TYPE_CHOICES)
    quantity = models.IntegerField()
    location = models.CharField(max_length=150)
    expiry_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

class FoodImage(models.Model):
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="food_images/")

class FoodRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    servings = models.IntegerField()
    pickup_time = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.receiver.username} → {self.food.name} ({self.status})"