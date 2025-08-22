

from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard1/', views.dashboard1_view, name='dashboard1'),
    path('logout/', views.logout_view, name='logout'),
    path('', include('pwa.urls')),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("register/", views.register, name="register"),
    path("setting/", views.setting, name="setting"),
    path('update-sell-rate/', views.update_sell_rate, name='update_sell_rate'),
    path('get-balance/', views.update_sell_rate, name='get_balance'),
    path('send_money/', views.send_money, name='send_money'),
    path("get-transactions/", views.get_transactions, name="get_transactions"),
    path("booking/", views.booking, name="booking"),
    path('member-list/', views.member_list, name='member_list'),
    path('withdrawl-list/', views.withdrawal_list, name='withdrawl_list'),

]
