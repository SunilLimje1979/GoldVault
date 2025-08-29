

from django.urls import path,include
from . import views
urlpatterns = [
    path('manifest.json/<str:code>', views.manifest, name='manifest'),
    path('', views.login_view, name='login'),
    path('owner_registration/', views.owner_registration, name='owner_registration'),
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
    path('get_cities/', views.get_cities, name='get_cities'),
    
    #################################### Shekhar ##########################################
    path("get_transection_list/", views.get_transection_list, name="get_transection_list"),
    path("details_transection/<str:id>/", views.details_transection, name="details_transection"),
    path('buy_submit/', views.buy_submit, name='buy_submit'),
    path('faq/', views.faq, name='faq'),
    path('termsofuse/', views.termsofuse, name='termsofuse'),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),
    path('membershipagrement/', views.membershipagrement, name='membershipagrement'),
    path('support_contact/', views.support_contact, name='support_contact'),
    path('old_queries/', views.old_queries, name='old_queries'),
    path('raise_query/', views.raise_query, name='raise_query'),
    path('payment_update/', views.payment_update, name='payment_update'),
    path('change_pin/', views.change_pin, name='change_pin'),
    path('update_nominee/', views.update_nominee, name='update_nominee'),
    
    ##################################### Akash ############################################
    
    # path('member_transection_list/<str:user_code>/' , views.member_transection_list , name='member_transection_list'),
    path('member_transection_list/' , views.member_transection_list , name='member_transection_list'),
    path('member_withdrawl_list/', views.member_withdrawl_list , name='member_withdrawl_list'),
    path('update_withdraw_status/', views.update_withdraw_status , name='update_withdraw_status'),
    path('get_booking_list/' , views.get_booking_list , name='get_booking_list'),
    path('update_booking_status/' , views.update_booking_status , name='update_booking_status'),
    path('get_withdrawal_list/', views.get_withdrawal_list,name='get_withdrawal_list'),
    path('member_booking_list/' , views.member_booking_list , name='member_booking_list'),
    path('owner_qr/' , views.owner_qr , name='owner_qr'),
    path('generate_shop_qr_pdf/<str:ClientCode>/', views.generate_shop_qr_pdf , name='generate_shop_qr_pdf'),

    
]
