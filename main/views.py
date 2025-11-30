from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, FoodItemForm
from .models import Profile, FoodItem
from django.contrib import messages
from .models import FoodRequest
from django.core.mail import send_mail
from django.db.models import Q
from .forms import UserRegisterForm, FoodItemForm, ProfileEditForm


# --- Home Page ---
def home_view(request):
    return render(request, 'main/home.html')

# --- Register User ---
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            role = form.cleaned_data['role']
            phone = form.cleaned_data['phone']

            Profile.objects.create(
                user=user,
                role=role,
                phone=phone
            )
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'main/register.html', {'form': form})


# --- Login User ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'main/login.html', {'error': 'Invalid username or password'})
    return render(request, 'main/login.html')

# --- Logout User ---
def logout_view(request):
    logout(request)
    return redirect('login')

# --- Dashboard & About ---
def dashboard_view(request):
    return render(request, 'main/dashboard.html')

def about_view(request):
    return render(request, 'main/about.html')

# --- Add Food (Donor) ---
@login_required
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)

        if form.is_valid():
            food = form.save(commit=False)
            food.donor = request.user  # assign donor
            food.save()  # save main food + single image
            return redirect('food_list')
        else:
            print(form.errors)  # debug

    else:
        form = FoodItemForm()

    return render(request, 'main/add_food.html', {'form': form})


# --- Food Detail ---
def food_detail_view(request, id):
    food = get_object_or_404(FoodItem, id=id)

    similar_foods = FoodItem.objects.filter(
        food_type=food.food_type,
        status='available'
    ).exclude(id=food.id)[:3]

    return render(request, 'main/food_detail.html', {
        'food': food,
        'similar_foods': similar_foods
    })



# --- Food List ---
def food_list(request):
    sort_by = request.GET.get("sort", "newest")

    if sort_by == "name":
        foods = FoodItem.objects.all().order_by("name")
    elif sort_by == "location":
        foods = FoodItem.objects.all().order_by("location")
    elif sort_by == "quantity":
        foods = FoodItem.objects.all().order_by("-quantity")
    else:  # default — newest first
        foods = FoodItem.objects.all().order_by("-id")

    return render(request, 'main/food_list.html', {
        'foods': foods,
        'sort_by': sort_by
    })


@login_required
def request_food(request, food_id):
    food_item = get_object_or_404(FoodItem, id=food_id)

    if request.method == "POST":
        # Get form data
        try:
            servings = int(request.POST.get("servings"))
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid number of servings.")
            return redirect('food_detail', id=food_id)

        pickup_time = request.POST.get("pickup_time")
        message = request.POST.get("message", "")  

        if not pickup_time:
            messages.error(request, "Please provide a pickup time.")
            return redirect('food_detail', id=food_id)

        # Check available servings
        if servings > food_item.quantity:
            messages.error(request, f"Only {food_item.quantity} servings are available.")
            return redirect('food_detail', id=food_id)

        # Create the FoodRequest
        food_request = FoodRequest.objects.create(
            receiver=request.user,
            food=food_item,
            servings=servings,
            pickup_time=pickup_time,
            message=message
        )

        # Send email to donor
        if food_item.donor.email:
            send_mail(
                subject="New Food Request Received",
                message=f"{request.user.username} has requested {servings} servings of your food item: {food_item.food_type}.",
                from_email="thavishkaa@gmail.com",
                recipient_list=[food_item.donor.email],
                fail_silently=False,
            )

        messages.success(request, "Request sent successfully!")
        return redirect('food_detail', id=food_id)

    # If not POST, redirect to food list
    return redirect('food_list')

@login_required
def donor_requests(request):
    # show only requests related to donor
    requests_list = FoodRequest.objects.filter(food__donor=request.user)
    return render(request, "main/donor_requests.html", {"requests": requests_list})

@login_required
def accept_request(request, req_id):
    req = get_object_or_404(FoodRequest, id=req_id)

    # Ensure only the donor can accept the request
    if req.food.donor != request.user:
        messages.error(request, "You cannot accept this request.")
        return redirect("donor_requests")

    # Reduce available quantity
    if req.servings <= req.food.quantity:
        req.food.quantity -= req.servings
        req.food.save()
    else:
        messages.error(request, "Not enough food available.")
        return redirect("donor_requests")

    # Update request status
    req.status = "accepted"
    req.save()

    # Mark food as claimed if quantity becomes zero
    if req.food.quantity == 0:
        req.food.status = "claimed"
        req.food.save()

    # -----------------------------
    #  GET DONOR PHONE NUMBER
    # -----------------------------
    donor_profile = Profile.objects.filter(user=req.food.donor).first()
    donor_phone = donor_profile.phone if donor_profile else "Not Provided"

    # -----------------------------
    #  SEND EMAIL TO RECEIVER
    # -----------------------------
    if req.receiver.email:
        send_mail(
            subject="Your Food Request Was Accepted!",
            message=(
                f"Great news {req.receiver.username}!\n\n"
                f"Your request for '{req.food.name}' has been accepted.\n"
                f"Approved Servings: {req.servings}\n\n"
                f"Pickup Location: {req.food.location}\n"
                f"Donor Contact Number: {donor_phone}\n\n"
                f"You can now call the donor to coordinate food pickup.\n\n"
                f"Thank you for using FoodShare!"
            ),
            from_email="thavishkaa@gmail.com",
            recipient_list=[req.receiver.email],
            fail_silently=False,
        )

    messages.success(request, "Request accepted successfully!")
    return redirect("donor_requests")



@login_required
def reject_request(request, req_id):
    req = get_object_or_404(FoodRequest, id=req_id)

    # Only donor can reject
    if req.food.donor != request.user:
        messages.error(request, "You cannot reject this request.")
        return redirect("donor_requests")

    req.status = "rejected"
    req.save()

    # Optional: notify the receiver
    if req.receiver.email:
        send_mail(
            subject="Your Food Request Was Rejected",
            message=(
                f"Hello {req.receiver.username},\n\n"
                f"Your request for '{req.food.food_type}' was rejected by the donor.\n"
                f"You can browse other available food items.\n\n"
                f"Thank you for using FoodShare!"
            ),
            from_email="thavishkaa@gmail.com",
            recipient_list=[req.receiver.email],
            fail_silently=False,
        )
 
    messages.success(request, "Request rejected successfully!")
    return redirect("donor_requests")


@login_required
def delete_food(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)

    # Only admin or the donor who added the food can delete
    if request.user.is_superuser or food.donor.user == request.user:
        food.delete()
        messages.success(request, "Food item deleted successfully.")
    else:
        messages.error(request, "You are not allowed to delete this food item.")

    return redirect('food_list')  
    

def available_food(request):
    query = request.GET.get('search', '').strip()
    food_type = request.GET.get('foodType', '')
    sort_by = request.GET.get('sortBy', 'newest')

    # Base queryset: only available foods
    foods = FoodItem.objects.filter(status='available')

    # Filter by search
    if query:
        foods = foods.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query)
        )

    # Filter by food type
    if food_type:
        foods = foods.filter(food_type=food_type)

    # Sorting
    if sort_by == 'expiring':
        foods = foods.order_by('expiry_time')
    elif sort_by == 'name':
        foods = foods.order_by('name')
    else:  # newest first
        foods = foods.order_by('-id')

    return render(request, 'main/available_food.html', {
        'foods': foods,
        'search_query': query,
        'food_type': food_type,
        'sort_by': sort_by,
    })

@login_required
def profile_edit(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'main/profile_edit.html', {'form': form})



