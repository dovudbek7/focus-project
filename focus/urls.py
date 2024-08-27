from django.contrib import admin
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_view
from . import views

app_name = 'focus'

urlpatterns = [
    path('', home, name='home'),
    path('postlist', post_list, name='post-list'),
    path('book/<int:year>/<int:month>/<int:day>/<slug:slug>/', PostDetailView.as_view(), name='post_details'),
    path('post/add', post_create, name='post_create'),
    path('post/update/<int:pk>/', post_update, name='post_update'),
    path('post/<int:pk>/delete/', post_delete, name='post_delete'),

    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path("password_change/", views.PasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", auth_view.PasswordChangeDoneView.as_view(),name="password_change_done",),
    path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_view.PasswordResetDoneView.as_view(), name="password_reset_done",),
    path("reset/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm",),
    path("reset/done/", auth_view.PasswordResetCompleteView.as_view(), name="password_reset_complete",),
]
