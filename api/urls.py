from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.SignUp.as_view(),name="signup"),
    path('login/',views.Login.as_view(),name="login"),
    path('dashboard/',views.Dashboard.as_view(),name="dashboard"),
    path('user/<pk>/',views.ShowUserById.as_view(),name="show-user"),
    
    path('admin-notifications/',views.AdminNotification.as_view(),name="admin-notification"),
    
    path('create-course/',views.CreateCourse.as_view(),name="create-course"),
    
    path('course/',views.JoinAndLeaveCourse.as_view(),name="course"),
    path('course/<pk>/',views.JoinAndLeaveCourse.as_view(),name="course-detail"),
]
