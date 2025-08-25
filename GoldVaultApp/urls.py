

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
    path('member_list/', views.member_list, name='member_list'),
    path('withdrawl_list/', views.withdrawal_list, name='withdrawl_list'),
    # path('member_transection_list/<str:user_code>/' , views.member_transection_list , name='member_transection_list'),
    path('member_transection_list/' , views.member_transection_list , name='member_transection_list'),
    path('member_withdrawl_list/', views.member_withdrawl_list , name='member_withdrawl_list'),
    path('update_withdraw_status/', views.update_withdraw_status , name='update_withdraw_status'),
    path('get_booking_list/' , views.get_booking_list , name='get_booking_list'),
    path('update_booking_status/' , views.update_booking_status , name='update_booking_status'),
    path('get_withdrawal_list/', views.get_withdrawal_list,name='get_withdrawal_list'),
    path('member_booking_list/' , views.member_booking_list , name='member_booking_list'),

]
