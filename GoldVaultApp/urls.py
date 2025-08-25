

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
    
    ##############################################################################
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
]
