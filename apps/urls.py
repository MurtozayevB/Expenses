from django.urls import path

from apps.views import (ExpenseCreateApiView, ExpenseDeleteApiView, ExpenseUpdateApiView, ExpenseDetailApiView, \
                        ExpenseListApiView, BalanceApiView, CategoryTypeListApiView, CategoryListApiView,
                        CategoryUpdateApiView, \
                        CategoryDeleteApiView, PasswordResetView,
                        ForgotPasswordAPIView, RegisterAPIView, ForgotPasswordCheckAPIView, RegisterCheckAPIView)

urlpatterns = [
    path('auth/register',RegisterAPIView.as_view() , name='register'),
    path('auth/register/check',RegisterCheckAPIView.as_view() , name='register-check'),
    path('auth/forgot-password',ForgotPasswordAPIView.as_view(), name='forgot_password' ),
    path('auth/verify-opt',ForgotPasswordCheckAPIView.as_view(), name='forgot_password_check' ),
    path('auth/reset-password',PasswordResetView.as_view(), name='reset-password'),
]

urlpatterns += [
    path('expenses', ExpenseCreateApiView.as_view()),
    path("expenses/delete/<int:pk>/", ExpenseDeleteApiView.as_view()),
    path("expenses/update/<int:pk>", ExpenseUpdateApiView.as_view()),
    path("expenses/detail<int:pk>/", ExpenseDetailApiView.as_view()),
    path("expenses/list", ExpenseListApiView.as_view()),
    path("expenses/balance", BalanceApiView.as_view()),
    path("category/<str:type>", CategoryTypeListApiView.as_view()),

]

urlpatterns +=[
    path("admin/category", CategoryListApiView.as_view()),
    path("admin/category/update/<int:pk>", CategoryUpdateApiView.as_view()),
    path("admin/category/delete/<int:pk>", CategoryDeleteApiView.as_view()),

]
