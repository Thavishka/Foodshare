from django.contrib import admin
from django.urls import path,include
from main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Food
    path('add-food/', views.add_food, name='add_food'),
    path('food-list/', views.food_list, name='food_list'),

    # Food Detail — FIXED PARAM NAME
    path('food-detail/<int:id>/', views.food_detail_view, name='food_detail'),

    # Other
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('about/', views.about_view, name='about'),

    path('request-food/<int:food_id>/', views.request_food, name='request_food'),

    path("requests/", views.donor_requests, name="donor_requests"),
    path("request/accept/<int:req_id>/", views.accept_request, name="accept_request"),
    path("request/reject/<int:req_id>/", views.reject_request, name="reject_request"),
    path('food/delete/<int:food_id>/', views.delete_food, name='delete_food'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
