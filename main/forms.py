from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, FoodItem


# --- Registration Form ---
class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, label="I am a")
    phone = forms.CharField(max_length=15, required=True, label="Phone Number")

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'phone','password1', 'password2', 'role']


# --- Food Item Form ---
class FoodItemForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity (Servings)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = FoodItem
        fields = [
            'name',
            'description',
            'food_type',
            'quantity',
            'location',
            'expiry_time',
            'image',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'food_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'})
        }
