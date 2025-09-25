from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from django.http import JsonResponse
import json
from urllib.parse import urlencode
from functools import wraps
from datetime import datetime
import pytz
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.urls import reverse
import os
import fitz  # PyMuPDF
from django.conf import settings
import io
import qrcode
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
################################## Manifest ####################################################
# def manifest(request,code):
#     # print("code",code)
#     check_res= requests.post("https://drishtis.app/DrishticrmMaster/api/get_app_master_by_code/",{"app_code":code})
#     # print(check_res.text)
#     if(check_res.json().get("message_code")==1000):
#         app_data= check_res.json().get("message_data")
#     # print(request.session['app_data'])
#     theme_color =app_data.get('theme_color', '#109787')  # Default to white
#     logo_url = app_data.get('logo_url', "/static/assets/img/DrishticrmLogo.png")  # Default logo
#     print(theme_color,logo_url)
    
#     manifest_data = {
#         "name": app_data.get('app_name', 'CRM'),
#         "short_name": app_data.get('app_short_name', 'CRM'),
#         "description": f"{app_data.get('app_name', 'CRM')} Web App",
#         "dir": "auto",
#         "lang": "en-US",
#         "start_url": f"/Drishticrm/login/?app_code={app_data.get('app_code')}",
#         "display": "standalone",
#         "orientation": "any",
#         "background_color": "#FFFFFF",
#         "theme_color": theme_color,
#         "icons": [
#             {
#                 "src": logo_url,
#                 "sizes": "512x512",
#                 "type": "image/png"
#             }
#         ]
#     }
#     print(manifest_data)
#     return JsonResponse(manifest_data)

# def manifest(request, code):
#     # ClientCode= "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
#     # ClientCode = request.session.get('ClientCode', None)
    
#     # ClientCode = code or request.session.get('ClientCode', None)
#     ClientCode = code
#     print(ClientCode,"53")
    
#     manifest_data = {
#         "name": "GoldVault",
#         "short_name": "Gold Vault",
#         "start_url": f"/GoldVault/?ClientCode={ClientCode}",  # ✅ dynamic
#         "display": "standalone",
#         "background_color": "#000000",
#         "theme_color": "#000000",
#         "orientation": "portrait",
#         "icons": [
#             {
#                 "src": "/GoldVault/static/assets/img/icon/192x192.png",
#                 "sizes": "192x192",
#                 "type": "image/png"
#             },
#             {
#                 "src": "/GoldVault/static/assets/img/icon/512x512.png",
#                 "sizes": "512x512",
#                 "type": "image/png"
#             }
#         ]
#     }
#     return JsonResponse(manifest_data)

def manifest(request, code):
    ClientCode = code
    print("ClientCode:", ClientCode)

    # Call API to get client info
    api_url = "https://www.gyaagl.app/goldvault_api/clientinfo"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    payload = {"ClientCode": ClientCode}

    # Defaults in case API fails
    business_name = "GoldVault"
    display_name = "Gold Vault"
    shop_logo = "/static/assets/img/icon/512x512.png"

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("API Response:", data)

        if data.get("message_code") == 1000 and data.get("message_data"):
            client_info = data["message_data"][0]

            # ✅ Use BusinessName & DisplayName
            business_name = client_info.get("BusinessName") or business_name
            display_name = client_info.get("DisplayName") or business_name

            # ✅ Use ShopPhotoURL if present
            if client_info.get("ShopPhotoURL"):
                shop_logo = client_info["ShopPhotoURL"]

    except requests.exceptions.RequestException as e:
        print("Error calling API:", e)
    except ValueError:
        print("Error parsing API response")

    # Build manifest
    manifest_data = {
        "name": business_name,
        # "short_name": display_name,
        "short_name": business_name,
        "start_url": f"/GoldVault/?ClientCode={ClientCode}",  # dynamic
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#000000",   # 🚨 not using API ThemeColor
        "orientation": "portrait",
        "icons": [
            {
                "src": shop_logo,
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": shop_logo,
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }

    return JsonResponse(manifest_data)
############## Decorator to check the user is loggined and it must Owner or not (UserType==1)

# def owner_required(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         user = request.session.get('user')
#         if not user or user.get('UserType') != '1':
#             request.session.flush()
#             return redirect('login')
#         return view_func(request, *args, **kwargs)
#     return wrapper

def owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.session.get('user')
        client_code = request.session.get('ClientCode')

        # Check: must have user and must be owner type (UserType = '1')
        if not user or str(user.get('UserType')) != '1':
            code = client_code  # preserve before flushing
            request.session.flush()

            login_url = reverse('login')
            if code:
                return redirect(f"{login_url}?ClientCode={code}")
            return redirect(login_url)

        return view_func(request, *args, **kwargs)
    return wrapper
##################################### Member Required ########################################
# def member_required(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         user = request.session.get('user')
#         if not user or user.get('UserType') != '0':  # check for member type
#             request.session.flush()
#             return redirect('login')
#         return view_func(request, *args, **kwargs)
#     return wrapper

def member_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.session.get('user')
        client_code = request.session.get('ClientCode')

        # Check: must have user and must be member type (UserType = '0')
        if not user or str(user.get('UserType')) != '0':
            code = client_code  # keep ClientCode safe before flush
            request.session.flush()

            login_url = reverse('login')
            if code:
                return redirect(f"{login_url}?ClientCode={code}")
            return redirect(login_url)

        return view_func(request, *args, **kwargs)
    return wrapper

######################################################################################
# def user_required(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         client_code = request.session.get('ClientCode', None)
#         user = request.session.get('user')
#         if not user:   # if user not in session
#             request.session.flush()
#             if client_code:
#                 # Redirect with ClientCode as query string
#                 return redirect(f"{reverse('login')}?ClientCode={client_code}")
#             else:
#                 return redirect('login')
#             # return redirect('login')
#         return view_func(request, *args, **kwargs)
#     return wrapper

def user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.session.get('user')
        client_code = request.session.get('ClientCode')

        if not user:
            # keep client_code safe before flushing
            code = client_code  

            request.session.flush()

            login_url = reverse('login')
            if code:
                return redirect(f"{login_url}?ClientCode={code}")
            return redirect(login_url)

        return view_func(request, *args, **kwargs)
    return wrapper

##############################################################################
def BASE(request):
    client_code = request.session.get('ClientCode')
    login_url = reverse('login')
    if client_code:
        return redirect(f"{login_url}?ClientCode={client_code}")
    return redirect(login_url)
        
    # return render(request, 'base.html')
############################# Forget Password ################################################
# def owner_registration(request):
#     if request.method == "POST":
#         data = {
#             "BusinessName": request.POST.get("BusinessName"),
#             "BusinessAddress": request.POST.get("BusinessAddress"),
#             "BusinessCityId": request.POST.get("BusinessCityId"),
#             "BusinessStateId": request.POST.get("BusinessStateId"),
#             "OwnerName": request.POST.get("OwnerName"),
#             "OwnerContact": request.POST.get("OwnerContact"),
#             "LoginPin": request.POST.get("LoginPin"),
#             "OwnerEmail": request.POST.get("OwnerEmail"),
#             "ShopPhotoURL": request.POST.get("ShopPhotoURL"),
#             "UPIID": request.POST.get("UPIID"),
#             "BankAccountName": request.POST.get("BankAccountName"),
#             "BankAccountNo": request.POST.get("BankAccountNo"),
#             "BankName": request.POST.get("BankName"),
#             "BranchName": request.POST.get("BranchName"),
#             "IFSCCode": request.POST.get("IFSCCode"),
#             "BranchAddress": request.POST.get("BranchAddress"),
#         }
#         print("Received Data:", data)  # ✅ Debugging

#         try:
#             api_url = "https://www.gyaagl.app/goldvault_api/clientregister"
#             headers = {
#                 "Accept": "application/json",
#                 "Content-Type": "application/json",
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#             }

#             response = requests.post(api_url, json=data, headers=headers, timeout=15)
#             response_data = response.json()
#             print("API Response:", response_data)  # ✅ Debugging

#             if response_data.get("message_code") == 1000:
#                 client_code = response_data["message_data"]["ClientCode"]

#                 # ✅ Store in session
#                 request.session['ClientCode'] = client_code

#                 # ✅ Redirect with client code
#                 redirect_url = f'https://gyaagl.club/GoldVault/?ClientCode="{client_code}"'
#                 messages.success(request, "Registration successful!")
#                 return redirect(redirect_url)
#             else:
#                 error_msg = response_data.get("message_text", "Something went wrong!")
#                 messages.error(request, f"Registration failed: {error_msg}")
#                 return render(request, "owner_registration.html", {"form_data": data})

#         except requests.exceptions.RequestException as e:
#             messages.error(request, f"API connection error: {str(e)}")
#             return render(request, "owner_registration.html", {"form_data": data})

#     return render(request, "owner_registration.html")

import os
from django.conf import settings
from PIL import Image
def owner_registration(request):
    states = []  # default empty

    # 🔹 Fetch states from API when page loads (GET request)
    try:
        api_url = "https://www.gyaagl.app/goldvault_api/liststates"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        payload = {"CountryId": "101"}
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        response_data = response.json()
        # print(response_data)

        if response_data.get("message_code") == 1000:
            states = response_data.get("message_data", [])
    except Exception as e:
        print("Error fetching states:", e)
        messages.error(request, "Could not load states list.")
        
    if request.method == "POST":
        business_name = request.POST.get("BusinessName")
        owner_contact = request.POST.get("OwnerContact")
        uploaded_file = request.FILES.get("ShopPhotoURL")

        shop_photo_url = None

        if uploaded_file:
            # Always save as PNG
            safe_business_name = business_name.replace(" ", "_").lower()
            # img_directory = os.path.join(settings.BASE_DIR, 'static', 'assets', 'company_logo')
            img_directory = os.path.join(settings.BASE_DIR, 'staticfiles', 'assets', 'company_logo')
            os.makedirs(img_directory, exist_ok=True)

            # File name always .png
            file_name = f"{owner_contact}.png"
            file_path = os.path.join(img_directory, file_name)

            # Open uploaded image with Pillow and convert to PNG
            image = Image.open(uploaded_file)
            image = image.convert("RGBA")  # ensure proper format
            image.save(file_path, "PNG")

            # Public URL (adjust domain as needed)
            shop_photo_url = f"https://gyaagl.club/GoldVault/static/assets/company_logo/{file_name}"

        # Collect data
        data = {
            "BusinessName": business_name,
            "BusinessAddress": request.POST.get("BusinessAddress"),
            "BusinessCityId": request.POST.get("BusinessCityId"),
            "BusinessStateId": request.POST.get("BusinessStateId"),
            "OwnerName": request.POST.get("OwnerName"),
            "OwnerContact": owner_contact,
            "LoginPin": request.POST.get("LoginPin"),
            "OwnerEmail": request.POST.get("OwnerEmail"),
            "ShopPhotoURL": shop_photo_url,   # final image URL
            "UPIID": request.POST.get("UPIID"),
            "BankAccountName": request.POST.get("BankAccountName"),
            "BankAccountNo": request.POST.get("BankAccountNo"),
            "BankName": request.POST.get("BankName"),
            "BranchName": request.POST.get("BranchName"),
            "IFSCCode": request.POST.get("IFSCCode"),
            "BranchAddress": request.POST.get("BranchAddress"),
        }

        print("Received Data:", data)

    # if request.method == "POST":
    #     data = {
    #         "BusinessName": request.POST.get("BusinessName"),
    #         "BusinessAddress": request.POST.get("BusinessAddress"),
    #         "BusinessCityId": request.POST.get("BusinessCityId"),
    #         "BusinessStateId": request.POST.get("BusinessStateId"),
    #         "OwnerName": request.POST.get("OwnerName"),
    #         "OwnerContact": request.POST.get("OwnerContact"),
    #         "LoginPin": request.POST.get("LoginPin"),
    #         "OwnerEmail": request.POST.get("OwnerEmail"),
    #         # "ShopPhotoURL": request.POST.get("ShopPhotoURL"),
    #         "ShopPhotoURL" : request.FILES.get("ShopPhotoURL"),
    #         "UPIID": request.POST.get("UPIID"),
    #         "BankAccountName": request.POST.get("BankAccountName"),
    #         "BankAccountNo": request.POST.get("BankAccountNo"),
    #         "BankName": request.POST.get("BankName"),
    #         "BranchName": request.POST.get("BranchName"),
    #         "IFSCCode": request.POST.get("IFSCCode"),
    #         "BranchAddress": request.POST.get("BranchAddress"),
    #     }
    #     print("Received Data:", data)

        try:
            api_url = "https://www.gyaagl.app/goldvault_api/clientregister"
            response = requests.post(api_url, json=data, headers=headers, timeout=15)
            response_data = response.json()
            print("API Response:", response_data)

            if response_data.get("message_code") == 1000:
                client_code = response_data["message_data"]["ClientCode"]

                # ✅ Store in session
                request.session['ClientCode'] = client_code

                # ✅ Redirect with client code
                redirect_url = f'https://gyaagl.club/GoldVault/?ClientCode={client_code}'
                messages.success(request, "Registration successful!")
                return redirect(redirect_url)
            else:
                error_msg = response_data.get("message_text", "Something went wrong!")
                messages.error(request, f"Registration failed: {error_msg}")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"API connection error: {str(e)}")

    return render(request, "owner_registration.html", {"states": states})

def get_cities(request):
    if request.method == "POST":
        import json
        body = json.loads(request.body.decode("utf-8"))
        state_id = body.get("StateId")
        
        # print("DEBUG: StateId =>", state_id)

        url = "https://www.gyaagl.app/goldvault_api/listcities"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        payload = {
            "CountryId": 101,
            "StateId": state_id
        }

        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        # # 🔹 Debug print full response
        # print("DEBUG: API Response =>", response_data)

        return JsonResponse(response_data)
############################# Forget Password ################################################
def forgot_password(request):
    return render(request, "forgot_password.html")

############################# Register ######################################
def register(request):
    return render(request, "register.html")

################################### Setting ############################################
@user_required
def setting(request):
    session_user = request.session.get("user", {}) or {}
    return render(request, "setting.html", {"user": session_user})

####################################### Login ####################################################
def login_view(request):
    # if request.method=='GET':
    #     ClientCode = request.GET.get("ClientCode")   # ✅ use clientid not client_id
    #     print("Client ID from URL:", ClientCode,"182")

    #     # Store in session
    #     request.session['ClientCode'] = ClientCode  
    #     print(request.session['ClientCode'],"186")
    #     return render(request, "base.html",{"ClientCode":ClientCode})
    
    if request.method == 'GET':
        # ClientCode = request.GET.get("ClientCode")
        # ClientCode = request.GET.get("ClientCode", "91c25409-84b4-11f0-9769-525400ce20fd")
        ClientCode = request.GET.get("ClientCode", "5dc0abf7-85de-4ede-abff-e7d53e3804b7")
        print("Client ID from URL:", ClientCode, "182")
        request.session['ClientCode'] = ClientCode  

        if ClientCode:
            # API call
            api_url = "https://www.gyaagl.app/goldvault_api/clientinfo"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            payload = {"ClientCode": ClientCode}

            try:
                response = requests.post(api_url, json=payload, headers=headers)
                response.raise_for_status()  # ensure HTTP 200 OK
                data = response.json()
                print("API Response:", data)

                if data.get("message_code") == 1000 and data.get("message_data"):
                    client_info = data["message_data"][0]

                    # Save in session
                    request.session['BusinessName'] = client_info.get("BusinessName")
                    request.session['ShopPhotoURL'] = client_info.get("ShopPhotoURL")
                    request.session['OwnerContact'] = client_info.get("OwnerContact")

                    # print("Stored in session:", request.session['DisplayName'], request.session['ShopPhotoURL'])
                else:
                    error_msg = data.get("message_text", "Failed to fetch client details.")
                    messages.error(request, error_msg)
                    print("API error:", error_msg)

            except requests.exceptions.RequestException as e:
                print("Error calling API:", e)
                messages.error(request, "Unable to connect to client info service. Please try again later.")
            except ValueError:
                print("Error parsing API response")
                messages.error(request, "Invalid response from client info service.")

        return render(request, "base.html", {
            "ClientCode": ClientCode,
            "BusinessName": request.session.get("BusinessName"),
            "ShopPhotoURL": request.session.get("ShopPhotoURL")
        })
    
    if request.method == 'POST':
        client_code = request.session.get('ClientCode', None)
        mobile = request.POST.get('mobile')
        pin = request.POST.get('pin_number')
        api_url = 'https://www.gyaagl.app/goldvault_api/login'
        payload = {
            "UserMobileNo": mobile,
            "UserPin": pin,
            "ClientCode": request.session.get('ClientCode', None)
        }
        print(payload,"197")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(data)

                if data.get("message_code") == 1000:
                    user = data["message_data"][0]
                    request.session['user'] = user
                    # messages.success(request, data.get("message_text", "Login successful."))

                    user_status = int(user.get("UserType", -1))
                    user_code = user.get("UserCode")

                    if user_status == 1:
                        return redirect("dashboard/")
                    elif user_status == 0:
                        return redirect("dashboard1/")
                    else:
                        messages.error(request, "Unknown user type. Please contact support.")
                        # return redirect("login_view")
                        return redirect(f"{reverse('login')}?ClientCode={client_code}")
                else:
                    messages.error(request, data.get("message_text", "Invalid mobile number or PIN."))
            else:
                messages.error(request, f"HTTP Error {response.status_code}")

        except Exception as e:
            print("Login Exception:", e)
            messages.error(request, "Unable to login. Please try again later.")

        return redirect(f"{reverse('login')}?ClientCode={client_code}")

##################################### Dashboard ################################################
@owner_required
def dashboard_view(request):
    # if 'user' not in request.session:
    #     return redirect('login')

    # user = request.session.get('user')
    # if user.get('UserType') != '1':
    #     request.session.flush()
    #     return redirect('login')
    
    # user_code = request.COOKIES.get("user_code")
    user_code = request.session.get('user').get('UserCode')
    print(user_code)
    ClientCode = request.session.get('ClientCode', None)
    print("ClientID:", ClientCode)
    
    # print("DEBUG: UserCode from cookie =>", user_code)

    # api_url = "https://www.gyaagl.app/goldvault_api/getbalances"
    # payload = {
    #     "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
    #     "UserCode": user_code
    # }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # stats = {"current_balance": 0, "total_value": 0, "total_invested": 0, "gain_loss": 0}
    # user = {"UserFullName": "", "UserMobileNo": ""}

    # try:
    #     response = requests.post(api_url, json=payload, headers=headers, timeout=10)
    #     print("DEBUG: Balance API response:", response.text)

    #     if response.status_code == 200:
    #         data = response.json()
    #         if data.get("message_code") == 1000 and data.get("message_data"):
    #             booking_list = data["message_data"].get("BookingId", [])
    #             if booking_list:
    #                 booking = booking_list[0]
    #                 stats["current_balance"] = booking.get("Balance", 0)
    #                 stats["product_weight"] = booking.get("ProductWeight", 0)
    #                 stats["total_invested"] = booking.get("AmountInvested", 0)
    #                 stats["gain_loss"] = booking.get("GainLoss", 0)
    #                 stats["total_withdrwal"] = booking.get("AmountWithdrawl", 0)
    #                 stats["withdrawl_weight"] = booking.get("WithdrawlWeight", 0)

    #             user_info = data["message_data"].get("UserDetails", {})
    #             user["UserFullName"] = user_info.get("UserFullName", "")
    #             user["UserMobileNo"] = user_info.get("UserMobileNo", "")

    #         else:
    #             print("API returned empty message_data or error:", data.get("message_text"))
    #     else:
    #         print("HTTP error:", response.status_code)
    # except Exception as e:
    #     print("Dashboard1 API Exception:", e)

    sell_rate=0
    rate_api_url = "https://www.gyaagl.app/goldvault_api/getrate"
    rate_payload = {
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
        "ClientCode": ClientCode
    }
    try:
        rate_response = requests.post(rate_api_url, json=rate_payload, headers=headers, timeout=10)
        print("DEBUG: Rate API response:", rate_response.text)

        if rate_response.status_code == 200:
            rate_data = rate_response.json()
            if rate_data.get("message_code") == 1000 and rate_data.get("message_data"):
                sell_rate = rate_data["message_data"][0].get("SellRate")
    except Exception as e:
        print("Dashboard Rate API Exception:", e)
    
    ##for booking and withdrawl summary
    # Get IST timezone
    ist = pytz.timezone("Asia/Kolkata")

    # Current time in IST
    today = datetime.now(ist)

    # Format for API (dd/mm/YYYY)
    date_str = today.strftime("%d/%m/%Y")

    print("today's date",date_str)

    bookings={}
    withdrawls={}
    getsummary_api_url = "https://www.gyaagl.app/goldvault_api/gettransummary"
    getsummary_payload = {
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
        "ClientCode": ClientCode,
        "TransactionDate":date_str,
    }
    try:
        getsummary_response = requests.post(getsummary_api_url, json=getsummary_payload, headers=headers, timeout=10)
        #print("DEBUG: getsummary API response:", getsummary_response.text)

        if getsummary_response.status_code == 200:
            getsummary_data = getsummary_response.json()
            if getsummary_data.get("message_code") == 1000 and getsummary_data.get("message_data"):
                summary_data=getsummary_data.get("message_data")
                print(summary_data)
                bookings = summary_data.get('Booking', {})
                withdrawls = summary_data.get('Withdrawl', {})

    except Exception as e:
        print("Dashboard Get Summary API Exception:", e)
        
    # ---------------- Get Notification Unread Counter ----------------
    unread_count = 0
    notif_api_url = "https://www.gyaagl.app/goldvault_api/notification/unreadcounter"
    notif_payload = {
        "ClientCode": ClientCode,
        "UserCode": user_code
    }

    try:
        notif_response = requests.post(notif_api_url, json=notif_payload, headers=headers, timeout=10)
        if notif_response.status_code == 200:
            notif_data = notif_response.json()
            if notif_data.get("message_code") == 1000 and notif_data.get("message_data") is not None:
                unread_count = notif_data["message_data"].get("UnreadCounter", 0)
    except Exception as e:
        print("Notification API Exception:", e)

    print(bookings)
    print(withdrawls)
    return render(request, "dashboard.html", {
        # "stats": stats,
        # "user": user,
        "sell_rate": sell_rate,
        "bookings":bookings,
        "withdrawls":withdrawls,
        "unread_count": unread_count
    })
    # return render(request, "dashboard.html", {"stats": stats, "user": user})
    
    
######################################## Dashboard 1 View ####################################################
@member_required
def dashboard1_view(request):
    # user_code = request.session.get('user').get('UserCode')
    # # print(user_code)

    # api_url = "https://www.gyaagl.app/goldvault_api/getbalances"
    # payload = {
    #     "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
    #     "UserCode": user_code
    #     # "UserCode": "14e2b5b6-7cb8-11f0-9769-525400ce20fd"
    # }
    
    user_code = request.session.get('user').get('UserCode')
    ClientCode = request.session.get('ClientCode', None)
    print("ClientID:", ClientCode)
    # print(user_code)

    api_url = "https://www.gyaagl.app/goldvault_api/getbalances"
    payload = {
        "ClientCode": ClientCode,
        "UserCode": user_code,
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
        # "UserCode": "14e2b5b6-7cb8-11f0-9769-525400ce20fd"
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    stats = {
        "current_balance": 0,
        "total_value": 0,
        "total_invested": 0,
        "gain_loss": 0
    }
    sell_rate = 0
    transactions = []  # Store transactions

    # ---------------- Get Balances API ----------------
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        # print("DEBUG: Balance API response:", response.text)

        if response.status_code == 200:
            data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                booking_list = data["message_data"].get("BookingId", [])
                if booking_list:
                    booking = booking_list[0]
                    stats["current_balance"] = booking.get("Balance", 0)
                    stats["product_weight"] = booking.get("ProductWeight", 0)
                    stats["total_invested"] = booking.get("AmountInvested", 0)
                    stats["gain_loss"] = booking.get("GainLoss", 0)
                    stats["total_withdrwal"] = booking.get("AmountWithdrawl", 0)
                    stats["withdrawl_weight"] = booking.get("WithdrawlWeight", 0)
    except Exception as e:
        print("Dashboard1 API Exception:", e)

    # ---------------- Get Rate API ----------------
    rate_api_url = "https://www.gyaagl.app/goldvault_api/getrate"
    # rate_payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"}
    rate_payload = {"ClientCode": ClientCode}

    try:
        rate_response = requests.post(rate_api_url, json=rate_payload, headers=headers, timeout=10)
        # print("DEBUG: Rate API response:", rate_response.text)

        if rate_response.status_code == 200:
            rate_data = rate_response.json()
            if rate_data.get("message_code") == 1000 and rate_data.get("message_data"):
                sell_rate = rate_data["message_data"][0].get("SellRate")
    except Exception as e:
        print("Dashboard Rate API Exception:", e)

    # ---------------- Get Transactions API ----------------
    transactions_api_url = "https://www.gyaagl.app/goldvault_api/gettransactions"
    trans_payload = {
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
        "ClientCode": ClientCode,
        "UserCode": user_code
        # "UserCode": "14e2b5b6-7cb8-11f0-9769-525400ce20fd"
    }

    try:
        trans_response = requests.post(transactions_api_url, json=trans_payload, headers=headers, timeout=10)
        # print("DEBUG: Transactions API response:", trans_response.text)

        if trans_response.status_code == 200:
            trans_data = trans_response.json()
            if trans_data.get("message_code") == 1000 and trans_data.get("message_data"):
                transactions = trans_data["message_data"][:5] # take latest 5
    except Exception as e:
        print("Transactions API Exception:", e)
        
        
        # ---------------- Get Notification Unread Counter API ----------------
    unread_count = 0
    notif_api_url = "https://www.gyaagl.app/goldvault_api/notification/unreadcounter"
    notif_payload = {
        "ClientCode": ClientCode,
        "UserCode": user_code
    }

    try:
        notif_response = requests.post(notif_api_url, json=notif_payload, headers=headers, timeout=10)
        # print("DEBUG: Notification API response:", notif_response.text)

        if notif_response.status_code == 200:
            notif_data = notif_response.json()
            if notif_data.get("message_code") == 1000 and notif_data.get("message_data") is not None:
                unread_count = notif_data["message_data"].get("UnreadCounter", 0)
    except Exception as e:
        print("Notification API Exception:", e)


    return render(request, "dashboard1.html", {
        "stats": stats,
        "sell_rate": sell_rate,
        "transactions": transactions,
        "unread_count": unread_count
    })
    
########################################### Get Transection List ##################################################
@member_required
def get_transection_list(request):
    user_code = request.session.get('user').get('UserCode')
    print("DEBUG: UserCode =>", user_code)
    
    ClientCode = request.session.get('ClientCode', None)


    transactions = []
    error = None

    transactions_api_url = "https://www.gyaagl.app/goldvault_api/gettransactions"
    trans_payload = {
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",  # keep fixed if API requires
        "ClientCode": ClientCode,
        "UserCode": user_code
        # "UserCode": "14e2b5b6-7cb8-11f0-9769-525400ce20fd"
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        trans_response = requests.post(transactions_api_url, json=trans_payload, headers=headers, timeout=10)
        # print("DEBUG: Transactions API response:", trans_response.text)

        if trans_response.status_code == 200:
            trans_data = trans_response.json()
            if trans_data.get("message_code") == 1000 and trans_data.get("message_data"):
                # ✅ Take all transactions
                transactions = trans_data["message_data"]
            else:
                error = trans_data.get("message_text", "No transactions found.")
        else:
            error = f"API Error: {trans_response.status_code}"

    except Exception as e:
        error = f"Transactions API Exception: {str(e)}"
        print(error)

    return render(
        request,
        "User/get_transection.html",
        {"user_code": user_code, "transactions": transactions, "error": error},
    )
########################################### Get Details Transection ###############################################
@member_required
def details_transection(request, id):
    client_code = request.session.get('ClientCode', None)
    user_code = request.session.get('user').get('UserCode')
    # client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"

    transaction = None
    error = None

    transactions_api_url = "https://www.gyaagl.app/goldvault_api/gettransactions"
    payload = {
        "ClientCode": client_code,
        "UserCode": user_code
        # "UserCode": "14e2b5b6-7cb8-11f0-9769-525400ce20fd"  # ✅ use logged-in user
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(transactions_api_url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                # ✅ find specific transaction by id
                transaction = next(
                    (txn for txn in data["message_data"] if str(txn["TransactionId"]) == str(id)),
                    None
                )
                print(transaction,"359")
                if not transaction:
                    error = f"Transaction {id} not found."
            else:
                error = data.get("message_text", "No transactions found.")
        else:
            error = f"{data.get("message_text")}"

    except Exception as e:
        error = f"Transactions API Exception: {str(e)}"

    return render(
        request,
        "User/details_transection.html",
        {"transaction": transaction, "error": error, "user_code": user_code},
    )


##################################### Get Transection #############################################    

def get_transactions(request):
    # user_code = request.session.get('user').get('UserCode')
    user_code = request.session.get('user').get('UserCode')
    # client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
    client_code = request.session.get('ClientCode', None)


    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    transactions = []
    try:
        response = requests.post(
            "https://www.gyaagl.app/goldvault_api/gettransactions",
            json={"ClientCode": client_code, "UserCode": user_code},
            headers=headers,
            timeout=10
        )
        print("DEBUG: Transactions API response:", response.text)

        if response.status_code == 200:
            data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                for tx in data["message_data"]:
                    transactions.append({
                        "id": tx.get("TransactionId"),
                        "type": tx.get("TransactionType"),
                        "date": tx.get("DispplayDate"),
                        "rate": tx.get("TransactionRate"),
                        "amount": tx.get("TransactionAmount"),
                        "weight": tx.get("Transactioneight"),
                        "status": tx.get("TransactionStatus"),
                    })
    except Exception as e:
        print("Transaction API Exception:", e)

    return JsonResponse({"transactions": transactions})
########################################### Buy Submit################################################
def buy_submit(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        weight = request.POST.get('weight')

        if not weight:
            messages.error(request, "Weight is invalid.")
            return redirect('dashboard1')

        try:
            weight_decimal = Decimal(weight).quantize(Decimal('0.00000'))  # Always 5 decimal places
        except:
            messages.error(request, "Weight is invalid.")
            return redirect('dashboard1')

        user = request.session.get('user', {})
        user_code = user.get('UserCode')
        # client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
        client_code = request.session.get('ClientCode', None)


        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # ---------------- Get Rate API ----------------
        rate_api_url = "https://www.gyaagl.app/goldvault_api/getrate"
        rate_payload = {"ClientCode": client_code}

        try:
            rate_response = requests.post(rate_api_url, json=rate_payload, headers=headers, timeout=10)

            if rate_response.status_code == 200:
                rate_data = rate_response.json()
                if rate_data.get("message_code") == 1000 and rate_data.get("message_data"):
                    sell_rate = rate_data["message_data"][0].get("SellRate")
                else:
                    messages.error(request, "Failed to fetch gold rate.")
                    return redirect('dashboard1')
            else:
                messages.error(request, "Rate API request failed.")
                return redirect('dashboard1')

        except Exception as e:
            print("Dashboard Rate API Exception:", e)
            messages.error(request, "Rate API error.")
            return redirect('dashboard1')

        # ---------------- Booking API ----------------
        booking_api_url = "https://www.gyaagl.app/goldvault_api/booking"
        booking_payload = {
            "ClientCode": client_code,
            "ProductDailyRate": sell_rate,
            "BookingAmount": amount,
            "BookingWeight": str(weight_decimal),
            "UserCode": user_code
        }
        
        print("booking Payload:" ,booking_payload)

        try:
            booking_response = requests.post(booking_api_url, json=booking_payload, headers=headers, timeout=10)
            if booking_response.status_code == 200:
                booking_data = booking_response.json()

                if booking_data.get("message_code") == 1000:
                    # Success → Show update_transaction.html with booking info
                    return render(request, "User/update_transaction.html", {
                        "booking": booking_data.get("message_data")
                    })
                else:
                    messages.error(request, booking_data.get("message_text", "Booking failed."))
                    return redirect('dashboard1')
            else:
                messages.error(request, "Booking API request failed.")
                return redirect('dashboard1')

        except Exception as e:
            print("Booking API Exception:", e)
            messages.error(request, "Booking API error.")
            return redirect('dashboard1')

    # If GET request → redirect back
    return redirect('dashboard1')
##################################### Payment Update ##################################################
def payment_update(request):
    if request.method == "POST":
        # client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
        client_code = request.session.get('ClientCode', None)
        user_code = request.session.get('user').get('UserCode')  # get from session
        booking_id = request.POST.get("BookingId")
        order_id = request.POST.get("OrderId")
        transaction_id = request.POST.get("utr")
        
          # Print all values (for debugging)
        print("Payment Update Data:")
        print("ClientCode:", client_code)
        print("UserCode:", user_code)
        print("OrderId:", order_id)
        print("BookingId:", booking_id)
        print("UTR / Transaction Id:", transaction_id)

        url = "https://www.gyaagl.app/goldvault_api/paymentupdate"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        payload = {
            "ClientCode": client_code,
            "UserCode": user_code,
            "BookingId": booking_id,
            "OrderId": order_id,
            "TransactionId": transaction_id
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json()
            print(data)

            # Handle success
            if data.get("message_code") == 1000:
                messages.success(request, data.get("message_text", "Payment updated successfully."))
            else:
                # Handle error messages from API
                messages.error(request, data.get("message_text", "Something went wrong!"))

        except Exception as e:
            messages.error(request, f"Error while updating payment: {str(e)}")

        # redirect back to dashboard1
        return redirect("dashboard1")

    else:
        messages.error(request, "Invalid request method.")
        return redirect("dashboard1")
########################################## Logout ##########################################################

def logout_view(request): 
    client_code = request.session.get('ClientCode', None)
    print(client_code)
    request.session.flush()  
    if client_code:
        # Redirect with ClientCode in query string
        return redirect(f"{reverse('login')}?ClientCode={client_code}")
    else:
        return redirect('login')
########################################### Change Pin ##############################################
@user_required
def change_pin(request): 
    user_code = request.session.get('user').get('UserCode')
    # client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
    client_code = request.session.get('ClientCode', None)

    print("User Code:", user_code) 

    if request.method == "POST":
        old_pin = request.POST.get("old_pin")
        new_pin = request.POST.get("new_pin")

        # Debug print
        print("Old PIN:", old_pin)
        print("New PIN:", new_pin)

        url = "https://www.gyaagl.app/goldvault_api/changepin"
        
        payload = {
            "UserCode": user_code,
            "ClientCode": client_code,
            "OldUserPin": old_pin,
            "NewUserPin": new_pin
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.gyaagl.app",
            "Referer": "https://www.gyaagl.app/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json()
            print("API Response:", data)

            if data.get("message_code") == 1000:
                messages.success(request, data.get("message_text", "PIN updated successfully."))
            else:
                messages.error(request, data.get("message_text", "Failed to update PIN."))

        except requests.exceptions.RequestException as e:
            print("API Error:", e)
            messages.error(request, "Unable to connect to server. Please try again later.")

        return redirect("change_pin")  # redirect back to same page

    return render(request, "User/change_pin.html")


######################################## Update Nominee ########################################
@user_required
def update_nominee(request): 
    # client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
    client_code = request.session.get('ClientCode', None)
    user_code = request.session.get('user').get('UserCode')
    # user_code = "14e2b5b6-7cb8-11f0-9769-525400ce20fd"  # replace with session later

    # ✅ Handle form submission (POST)
    if request.method == "POST":
        full_name = request.POST.get("NomineeFullName")
        relation = request.POST.get("NomieeRelation")
        dob = request.POST.get("NomineeDateofBirth")
        mobile = request.POST.get("NomieeMobileNo")
        pan = request.POST.get("NomieePanNo")
        aadhar = request.POST.get("NomieeAadharNo")
        address = request.POST.get("NomineeAddress")
        status = request.POST.get("NomineeStatus")   # optional
        is_minor = request.POST.get("NomieeIsMinorYN", "0")  # default 0

        payload = {
            "ClientCode": client_code,
            "UserCode": user_code,
            "NomieeIsMinorYN": is_minor,
            "NomieeRelation": relation,
            "NomieeMobileNo": mobile,
            "NomieePanNo": pan,
            "NomieeAadharNo": aadhar,
            "NomineeAddress": address,
            "NomineeDateofBirth": dob,
            "NomineeFullName": full_name,
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.gyaagl.app",
            "Referer": "https://www.gyaagl.app/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            response = requests.post("https://www.gyaagl.app/goldvault_api/updatenominee", json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("Update API Response:", data)
                if data.get("message_code") == 1000:
                    messages.success(request, data.get("message_text", "Nominee updated successfully."))
                else:
                    messages.error(request, data.get("message_text", "Failed to update nominee."))
            else:
                messages.error(request, f"HTTP Error {response.status_code}")
        except requests.exceptions.RequestException as e:
            print("API Error:", e)
            messages.error(request, "Unable to update nominee. Please try again later.")

        return redirect("update_nominee")  # redirect so messages persist

    # ✅ Handle fetching nominee data (GET)
    url = "https://www.gyaagl.app/goldvault_api/getnominee"
    payload = {
        "UserCode": user_code,
        "ClientCode": client_code
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    nominee_data = []
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # print("GetNominee API Response:", data)

            if data.get("message_code") == 1000:
                nominee_data = data.get("message_data", [])
                if not nominee_data:
                     pass
                    # messages.info(request, data.get("message_text", "No nominee found. Please add nominee."))
            else:
                 pass
                # messages.error(request, data.get("message_text", "Failed to fetch nominee details."))
        else:
             pass
            # messages.error(request, f"HTTP Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("API Error:", e)
        messages.error(request, "Unable to connect to server. Please try again later.")

    return render(request, "User/update_nominee.html", {"nominees": nominee_data})
############################################# Send Money ####################################################
@member_required
def send_money(request):
    client_code = request.session.get('ClientCode', None)
    if request.method == 'POST':
        # user_code = request.COOKIES.get("user_code")
        user_code = request.session.get('user').get('UserCode')
        print(user_code)
        
        withdraw_amount = request.POST.get('withdraw_amount')
        withdraw_weight = request.POST.get('withdraw_weight')    
         # Validate and format withdraw_weight
        try:
            withdraw_weight = "{:.5f}".format(float(withdraw_weight))
        except (TypeError, ValueError):
            messages.error(request, "Invalid withdraw weight.")
            return redirect('dashboard1')
        
        print(withdraw_weight)
        
        api_url = 'https://www.gyaagl.app/goldvault_api/withdrawlrequest'  
        

        payload = {
            # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
            "ClientCode": client_code,
            "UserCode": user_code,
            "ProductDailyRate": 10000,            
            "WithdrawlWeight": withdraw_weight,
            "WithdrawlAmount": withdraw_amount
        }
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.gyaagl.app",
            "Referer": "https://www.gyaagl.app/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                print(data)
                if data.get("message_code") == 1000:
                    messages.success(request, "Withdraw Request send successfully.")
                    return redirect("dashboard1")
                else:
                    messages.error(request, data.get("message_text", "Something went wrong."))
                    return redirect("dashboard1")
            else:
                messages.error(request, f"HTTP {response.status_code}")
                return redirect("dashboard1")
        except Exception as e:
            print("Exception:", e)
            messages.error(request, str(e))
            return redirect("dashboard1")
    return render(request, "dashboard1.html")

############################################ FAQ #########################################################
import html
@user_required
def faq(request):
    user_code = request.session.get('user', {}).get('UserCode')
    client_code = request.session.get('ClientCode', None)
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"

    payload = {"ClientCode": client_code, "TextType": "4"}
    # payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "4"}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()  # ✅ raises HTTPError if not 200

        data = resp.json()
        if data.get("message_code") == 1000 and data.get("message_data"):
            faq_data = data["message_data"][0]
            return render(request, "User/FAQ.html", {
                "user_code": user_code,
                "faq_title": faq_data.get("TextTitle", "FAQ"),
                "faq_html": html.unescape(faq_data.get("HTMLText", "")),
                "last_updated": faq_data.get("LastUpdatedOn", ""),
            })
        else:
            error = data.get("message_text", "Unexpected API response.")
    except requests.exceptions.RequestException as e:
        error = f"Request error: {e}"
    except Exception as e:
        error = f"Error: {e}"

    return render(request, "User/FAQ.html", {"error": error})
########################################## Terms of Use ##################################################################
@user_required
def termsofuse(request):
    user_code = request.session.get('user', {}).get('UserCode')
    client_code = request.session.get('ClientCode', None)
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"

    # payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "1"}
    payload = {"ClientCode": client_code, "TextType": "1"}
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()  # ✅ raises HTTPError if not 200

        data = resp.json()
        if data.get("message_code") == 1000 and data.get("message_data"):
            faq_data = data["message_data"][0]
            return render(request, "User/FAQ.html", {
                "user_code": user_code,
                "faq_title": faq_data.get("TextTitle", "FAQ"),
                "faq_html": html.unescape(faq_data.get("HTMLText", "")),
                "last_updated": faq_data.get("LastUpdatedOn", ""),
            })
        else:
            error = data.get("message_text", "Unexpected API response.")
    except requests.exceptions.RequestException as e:
        error = f"Request error: {e}"
    except Exception as e:
        error = f"Error: {e}"

    return render(request, "User/FAQ.html", {"error": error})
########################################## Terms of Use ##################################################################
@user_required
def privacypolicy(request):
    client_code = request.session.get('ClientCode', None)
    user_code = request.session.get('user', {}).get('UserCode')
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"

    # payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "2"}
    payload = {"ClientCode": client_code, "TextType": "2"}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()  # ✅ raises HTTPError if not 200

        data = resp.json()
        if data.get("message_code") == 1000 and data.get("message_data"):
            faq_data = data["message_data"][0]
            return render(request, "User/FAQ.html", {
                "user_code": user_code,
                "faq_title": faq_data.get("TextTitle", "FAQ"),
                "faq_html": html.unescape(faq_data.get("HTMLText", "")),
                "last_updated": faq_data.get("LastUpdatedOn", ""),
            })
        else:
            error = data.get("message_text", "Unexpected API response.")
    except requests.exceptions.RequestException as e:
        error = f"Request error: {e}"
    except Exception as e:
        error = f"Error: {e}"

    return render(request, "User/FAQ.html", {"error": error})    
########################################### Membership Agreement ######################################################
@user_required
def membershipagrement(request):
    user_code = request.session.get('user', {}).get('UserCode')
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"
    client_code = request.session.get('ClientCode', None)

    # payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "3"}
    payload = {"ClientCode": client_code, "TextType": "3"}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()  # ✅ raises HTTPError if not 200

        data = resp.json()
        if data.get("message_code") == 1000 and data.get("message_data"):
            faq_data = data["message_data"][0]
            return render(request, "User/FAQ.html", {
                "user_code": user_code,
                "faq_title": faq_data.get("TextTitle", "FAQ"),
                "faq_html": html.unescape(faq_data.get("HTMLText", "")),
                "last_updated": faq_data.get("LastUpdatedOn", ""),
            })
        else:
            error = data.get("message_text", "Unexpected API response.")
    except requests.exceptions.RequestException as e:
        error = f"Request error: {e}"
    except Exception as e:
        error = f"Error: {e}"

    return render(request, "User/FAQ.html", {"error": error})    
########################################### Support Contact ######################################################
@user_required
def support_contact(request):
    user_code = request.session.get('user', {}).get('UserCode')
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"
    client_code = request.session.get('ClientCode', None)

    # payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "5"}
    payload = {"ClientCode": client_code, "TextType": "5"}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()  # ✅ raises HTTPError if not 200

        data = resp.json()
        if data.get("message_code") == 1000 and data.get("message_data"):
            faq_data = data["message_data"][0]
            return render(request, "User/FAQ.html", {
                "user_code": user_code,
                "faq_title": faq_data.get("TextTitle", "FAQ"),
                "faq_html": html.unescape(faq_data.get("HTMLText", "")),
                "last_updated": faq_data.get("LastUpdatedOn", ""),
            })
        else:
            error = data.get("message_text", "Unexpected API response.")
    except requests.exceptions.RequestException as e:
        error = f"Request error: {e}"
    except Exception as e:
        error = f"Error: {e}"

    return render(request, "User/FAQ.html", {"error": error})  
######################################## Old Quiries#############################################
@user_required
def old_queries(request):
    user = request.session.get('user', {})
    user_code = user.get('UserCode')
    user_name = user.get('UserFullName')   # ✅ fetch name
    # client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
    client_code = request.session.get('ClientCode', None)
    api_url = "https://www.gyaagl.app/goldvault_api/listqueries"

    payload = {
        "ClientCode": client_code,
        "UserCode": user_code
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("message_code") == 1000:
                return render(request, "User/old_queries.html", {
                    "queries": data.get("message_data", []),
                    "user_name": user_name   # ✅ send to template
                })
            else:
                return render(request, "User/old_queries.html", {
                    "error": data.get("message_text"),
                    "user_name": user_name
                })
        return render(request, "User/old_queries.html", {
            "error": f"HTTP {response.status_code}",
            "user_name": user_name
        })
    except Exception as e:
        return render(request, "User/old_queries.html", {
            "error": str(e),
            "user_name": user_name
        })
###################################### Raise Query ######################################################
@user_required
def raise_query(request):
    user_code = request.session.get('user', {}).get('UserCode')
    # client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
    client_code = request.session.get('ClientCode', None)

    if request.method == "POST":
        query_subject = request.POST.get("QuerySubject")
        query_text = request.POST.get("QueryText")

        url = "https://www.gyaagl.app/goldvault_api/raisequery"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        payload = {
            "ClientCode": client_code,
            "UserCode": user_code,
            "QuerySubject": query_subject,
            "QueryText": query_text,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json()
            print(data)
            if data.get("message_code") == 1000:
                # ✅ Success → Redirect to settings page with message
                messages.success(request, data.get("message_text", "Query submitted successfully!"))
                return redirect("old_queries")  # make sure you have settings url name
            else:
                # ❌ Failure → Show error message on same page
                messages.error(request, data.get("message_text", "Failed to submit query."))
                return render(request, "User/raise_query.html", {
                    "user_code": user_code,
                    "QuerySubject": query_subject,
                    "QueryText": query_text
                })

        except Exception as e:
            messages.error(request, f"Error while submitting query: {str(e)}")
            return render(request, "User/raise_query.html", {
                "user_code": user_code,
                "QuerySubject": query_subject,
                "QueryText": query_text
            })

    return render(request, "User/raise_query.html", {"user_code": user_code})

####################################### Register #########################################################
def register(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile_number')
        pin = request.POST.get('pin_number')
        name = request.POST.get('full_name')
        client_code = request.session.get('ClientCode', None)

        api_url = 'https://www.gyaagl.app/goldvault_api/register'
        payload = {
            "UserMobileNo": mobile,
            "UserPin": pin,
            "FullName": name,
            "ClientCode": client_code
            # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.gyaagl.app",
            "Referer": "https://www.gyaagl.app/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            print("Status:", response.status_code)
            print("Response:", response.text)

            if response.status_code == 200:
                data = response.json()
                if data.get("message_code") == 1000:
                    user = data["message_data"][0]
                    messages.success(request, data.get("message_text", "Registration successful."))
                    # return render(request, "base.html", {"user": user})
                    login_url = reverse('login')
                    if client_code:
                        return redirect(f"{login_url}?ClientCode={client_code}")
                    return redirect(login_url)
                
                else:
                    messages.error(request, data.get("message_text", "Registration failed."))
            else:
                messages.error(request, f"HTTP Error {response.status_code}")

        except Exception as e:
            print("Exception:", e)
            messages.error(request, "Something went wrong. Please try again later.")

    return render(request, "register.html")
########################################## Update Sell Rate ######################################################
@owner_required
def update_sell_rate(request):
    if request.method == 'POST':
        sell_rate = request.POST.get('sell_rate')
        api_url = 'https://www.gyaagl.app/goldvault_api/dailyrate'  
        client_code = request.session.get('ClientCode', None)

        payload = {
            # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
            "ClientCode": client_code,
            "SellRate": sell_rate
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.gyaagl.app",
            "Referer": "https://www.gyaagl.app/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            print("Status:", response.status_code)
            print("Response:", response.text)

            if response.status_code == 200:
                data = response.json()
                if data.get("message_code") == 1000:
                    messages.success(request,"Gold rate updated successfully")
                    return redirect(dashboard_view)
                else:
                    messages.info(request,data.get("message_text"))
                    return redirect(dashboard_view)
                    return render(request, "dashboard.html", {"error": data.get("message_text")})
            else:
                messages.error(request,f"HTTP {response.status_code}")
                return redirect(dashboard_view)
                return render(request, "dashboard.html", {"error": f"HTTP {response.status_code}"})

        except Exception as e:
            print("Exception:", e)
            messages.error(request,str(e))
            return redirect(dashboard_view)
            return render(request, "dashboard.html", {"error": str(e)})

    return redirect(dashboard_view)


#################################### GET Rate ###########################################################

def get_rate(request):
    api_url = "https://www.gyaagl.app/goldvault_api/getrate"
    client_code = request.session.get('ClientCode', None)
    payload = {"ClientCode": client_code}

    # payload = {
    #     "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
    # }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        print("Status:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:
            data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                sell_rate = data["message_data"][0].get("SellRate")
                print(sell_rate)
                return render(request, "dashboard.html", {
                    "sell_rate": sell_rate,
                    "data": data
                })
            else:
                return render(request, "dashboard.html", {
                    "error": data.get("message_text", "Unknown error")
                })
        else:
            return render(request, "dashboard.html", {
                "error": f"HTTP {response.status_code}"
            })

    except Exception as e:
        print("Exception:", e)
        return render(request, "dashboard.html", {"error": str(e)})

################################## Booking ###################################################
def booking(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        weight = request.POST.get('weight')
        product_daily_rate = request.POST.get('product_daily_rate', '9807')
        # user_code = "14e2b5b6-7cb8-11f0-9769-525400ce20fd"
        user_code = request.session.get('user', {}).get('UserCode')
        client_code = request.session.get('ClientCode', None)

        api_url = 'https://www.gyaagl.app/goldvault_api/booking'
        payload = {
            # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
            "ClientCode": client_code,
            "ProductDailyRate": product_daily_rate,
            "BookingAmount": amount,
            "BookingWeight": weight,
            "UserCode": user_code
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.gyaagl.app",
            "Referer": "https://www.gyaagl.app/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("message_code") == 1000:
                    return redirect(f'/dashboard1/')
                else:
                    params = urlencode({"error": data.get("message_text")})
                    return redirect(f'/dashboard1/?{params}')
            else:
                params = urlencode({"error": f"HTTP {response.status_code}"})
                return redirect(f'/dashboard1/?{params}')

        except Exception as e:
            params = urlencode({"error": str(e)})
            return redirect(f'/dashboard1/?{params}')
    return redirect('/dashboard1/')

###################################### Get Balance ########################################################
def get_balance(request):
    # user_code = request.COOKIES.get("user_code")
    user_code = request.session.get('user').get('UserCode')
    print(user_code)
    api_url = "https://www.gyaagl.app/goldvault_api/getbalances"
    client_code = request.session.get('ClientCode', None)

    payload = {
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
        "ClientCode": client_code,
        "UserCode": user_code
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    stats = {
        "current_balance": "0.00",
        "total_value": "0.00",
        "total_invested": "0.00",
        "gain_loss": "0.00",
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("message_code") == 1000:
                message_data = data.get("message_data", [{}])[0]
                stats = {
                    "current_balance": message_data.get("CurrentBalance", "0.00"),
                    "total_value": message_data.get("TodaysValue", "0.00"),  # key matches template
                    "total_invested": message_data.get("TotalInvested", "0.00"),
                    "gain_loss": message_data.get("GainLoss", "0.00"),
                }
            else:
                print("API Error:", data.get("message_text"))
        else:
            print("HTTP Error:", response.status_code)
    except Exception as e:
        print("Exception:", e)
    return render(request, "dashboard1.html", {"stats": stats})

########################################## Member List ####################################################
@owner_required
def member_list(request):
    api_url = "https://www.gyaagl.app/goldvault_api/getmembers"
    client_code = request.session.get('ClientCode', None)
    payload = {"ClientCode": client_code}
    # payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        data = response.json() if response.status_code == 200 else {}
    except Exception as e:
        data = {"message_code": 0, "message_text": str(e), "message_data": []}

    members = data.get("message_data", [])

    if request.method == "GET":
        print(members)
        return render(request, "owner/member_list.html", {"members": members})

    if data.get("message_code") == 1000:
        return JsonResponse({"status": "success", "members": members})
    return JsonResponse({"status": "error", "message": data.get("message_text")})

################################## Withdrawal List #####################################################
def withdrawal_list(request):
    api_url = "https://www.gyaagl.app/goldvault_api/getwithdrawls"
    client_code = request.session.get('ClientCode', None)
    payload = {"ClientCode": client_code}
    # payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"}
    headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.gyaagl.app",
            "Referer": "https://www.gyaagl.app/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        response_text = response.text.strip()

        # clean JSON
        first_brace = response_text.find("{")
        last_brace = response_text.rfind("}")
        clean_json = response_text[first_brace:last_brace+1] if first_brace != -1 else "{}"
        data = json.loads(clean_json)

        if data.get("message_code") == 1000:
            members = [
                {
                    "name": m.get("UserFullName"),
                    "mobile": m.get("UserMobileNo"),
                    "product_rate": m.get("ProductDailyRate"),
                    "withdraw_amount": m.get("WithdrawAmount"),
                    "withdraw_weight": m.get("WithdrawWeight"),
                }
                for m in data.get("message_data", [])
            ]
            return render(request, "withdrawl_list.html", {"members": members})
        else:
            return render(request, "withdrawl_list.html", {"error": data.get("message_text")})

    except Exception as e:
        return render(request, "withdrawl_list.html", {"error": str(e)})


##############################################################################################









###########Owner-member-transaction list
@owner_required
# def member_transection_list(request,user_code):
def member_transection_list(request):
    if not request.method =='POST':
        return redirect(dashboard_view)
    
    user_code = request.POST['UserCode']
    UserFullName = request.POST['UserFullName']
    UserMobileNo = request.POST['UserMobileNo']
    client_code = request.session.get('ClientCode', None)
    # UserStatus = request.POST['UserStatus']
    Balance = request.POST['Balance']
    member = {"name":UserFullName,"mobileno":UserMobileNo,"Balance":Balance}

    transactions = []
    error = None

    transactions_api_url = "https://www.gyaagl.app/goldvault_api/gettransactions"
    trans_payload = {
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",  # keep fixed if API requires
        "ClientCode": client_code, 
        "UserCode": user_code
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        trans_response = requests.post(transactions_api_url, json=trans_payload, headers=headers, timeout=10)
        print("DEBUG: Transactions API response:", trans_response.text)

        if trans_response.status_code == 200:
            trans_data = trans_response.json()
            if trans_data.get("message_code") == 1000 and trans_data.get("message_data"):
                # ✅ Take all transactions
                transactions = trans_data["message_data"]
            else:
                error = trans_data.get("message_text", "No transactions found.")
        else:
            error = f"API Error: {trans_response.status_code}"

    except Exception as e:
        error = f"Transactions API Exception: {str(e)}"
        print(error)

    return render(
        request,
        "owner/member_transaction_list.html",
        {"user_code": user_code,'member': member,"transactions": transactions, "error": error},
    )

@owner_required
def member_transection_details(request, id):
    user_code = request.session.get('user').get('UserCode')
    # client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
    client_code = request.session.get('ClientCode', None)

    transaction = None
    error = None

    transactions_api_url = "https://www.gyaagl.app/goldvault_api/gettransactions"
    payload = {
        "ClientCode": client_code,
        "UserCode": "14e2b5b6-7cb8-11f0-9769-525400ce20fd"  # ✅ use logged-in user
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(transactions_api_url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                # ✅ find specific transaction by id
                transaction = next(
                    (txn for txn in data["message_data"] if str(txn["TransactionId"]) == str(id)),
                    None
                )
                print(transaction,"359")
                if not transaction:
                    error = f"Transaction {id} not found."
            else:
                error = data.get("message_text", "No transactions found.")
        else:
            error = f"{data.get("message_text")}"

    except Exception as e:
        error = f"Transactions API Exception: {str(e)}"

    return render(
        request,
        "owner/member_transection_details.html",
        {"transaction": transaction, "error": error, "user_code": user_code},
    )

######################################## Member-withdrawl-list
@owner_required
def member_withdrawl_list(request):
    members = []
    error = None
    client_code = request.session.get('ClientCode', None)

    api_url = "https://www.gyaagl.app/goldvault_api/getwithdrawls"
    payload = {
        "ClientCode": client_code
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        #print("DEBUG: Withdrawls API response:", response.text)

        # response_text = response.text.strip()

        # # clean JSON
        # first_brace = response_text.find("{")
        # last_brace = response_text.rfind("}")
        # clean_json = response_text[first_brace:last_brace+1] if first_brace != -1 else "{}"
        # data = json.loads(clean_json)
        data = response.json()

        if data.get("message_code") == 1000:
            # data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                members = data["message_data"]   # ✅ store withdrawl list in members
            else:
                error = data.get("message_text", "No withdrawls found.")
        else:
            error = f"{data.get("message_text")}"

    except Exception as e:
        error = f"Withdrawl API Exception: {str(e)}"
        print(error)

    # for m in members:
    #     m['OrderStatus']='3'
    #     print(m)
    return render(
        request,
        "owner/member_withdrawl_list.html",
        {"members": members, "error": error},
    )


# @csrf_exempt   # if you already use CSRF token in template you can remove this
# def update_withdraw_status(request):
#     if request.method == "POST":
#         withdraw_id = request.POST.get("withdraw_id")
#         action = request.POST.get("action")  # "approve" or "reject"
#         usercode = request.POST.get("usercode")
#         print(request.POST)
#         if not withdraw_id or not action:
#             return JsonResponse({"success": False, "message": "Missing parameters"})

#         try:
            
#             return JsonResponse({"success": True})
#         except Exception as e:
#             return JsonResponse({"success": False, "message": str(e)})

#     return JsonResponse({"success": False, "message": "Invalid request"})

@csrf_exempt   # remove if you already handle CSRF in template
def update_withdraw_status(request):
    if request.method == "POST":
        client_code = request.session.get('ClientCode', None)
        withdraw_id = request.POST.get("withdraw_id")
        action = request.POST.get("action")  # "approve" or "reject"
        usercode = request.POST.get("usercode")  # passed from template hidden field

        print("DEBUG POST:", request.POST)

        if not withdraw_id or not action or not usercode:
            return JsonResponse({"success": False, "message": "Missing parameters"})

        try:
            # Build WithdrawlStatus from action
            status_map = {
                "approve": "APPROVED",
                "reject": "REJECTED",
                "deliver": "DELIVERED"   # if you add delivery action later
            }
            withdraw_status = status_map.get(action.lower(), "PENDING")

            # API endpoint
            api_url = "https://www.gyaagl.app/goldvault_api/updatewithdrawl"

            # Payload
            payload = {
                "UserCode": usercode,
                "WithdrawalId": withdraw_id,
                "WithdrawalStatus": withdraw_status,
                "ClientCode": client_code,
                # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
            }

            headers = {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Origin": "https://www.gyaagl.app",
                "Referer": "https://www.gyaagl.app/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            # Make request
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            print(response.text)
            response_text = response.text.strip()
            first_brace = response_text.find("{")
            last_brace = response_text.rfind("}")
            clean_json = response_text[first_brace:last_brace+1] if first_brace != -1 else "{}"
            data = json.loads(clean_json)
            
            if response.status_code == 200 and data.get("message_code") == 1000:
                return JsonResponse({"success": True, "message": f"{withdraw_status} successfully"})
                # return JsonResponse({"success": True, "message": "Status updated successfully"})
            else:
                return JsonResponse({
                    "success": False,
                    "message": data.get("message_text", f"API error {response.status_code}")
                })

        except Exception as e:
            return JsonResponse({"success": False, "message": f"API Exception: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request"})

################################### Get Booking List ##############################################
@owner_required
def get_booking_list(request):
    date = request.GET.get('date')
    print("844",date)
    if not date :
        # today = datetime.today()
        # Format for API (dd/mm/YYYY)
        # Get IST timezone
        ist = pytz.timezone("Asia/Kolkata")

        # Current time in IST
        today = datetime.now(ist)

        # Format for API (dd/mm/YYYY)
        date_str = today.strftime("%d/%m/%Y")

        print("today's date",date_str)
        # date_str = today.strftime("%d/%m/%Y")
        # Format for input field (YYYY-mm-dd)
        date = today.strftime("%Y-%m-%d")
        # date_str = "23/08/2025"
    
    else:
        date_str = date # example: "2025-08-24"
        if date_str:  
            try:
                y, m, d = date_str.split('-')   # "2025", "08", "24"
                date_str = f"{d}/{m}/{y}"       # "24/08/2025"
            except ValueError:
                # if format is not correct, keep as is
                pass
    
    print("863",date)
    print("864",date_str)
    bookings = {}
    error = None

    client_code = request.session.get('ClientCode', None)
    
    api_url = "https://www.gyaagl.app/goldvault_api/getcollection"
    payload = {
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
        "ClientCode": client_code,
        "TransactionDate":date_str
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        # print("DEBUG: Bookings API response:", response.text)
        data = response.json()
        if data.get("message_code") == 1000:
            # data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                bookings_data = data["message_data"]   # ✅ store booking list in bookings
                bookings= bookings_data.get('Booking', {})
            else:
                error = data.get("message_text", "No Bookings found.")
        else:
            error = f"{data.get("message_text")}"

    except Exception as e:
        error = f"Booking API Exception: {str(e)}"
        print(error)

    #print(bookings)
    return render(
        request,
        "owner/getall_booking_list.html",
        {"bookings": bookings,'date':date ,"error": error,},
    )

#################################  Update Booking status #############################################
@csrf_exempt   # remove if you already handle CSRF in template
def update_booking_status(request):
    if request.method == "POST":
        client_code = request.session.get('ClientCode', None)
        booking_id = request.POST.get("booking_id")
        action = request.POST.get("action")  # "approve" or "reject"
        OrderId = request.POST.get("OrderId")  # passed from template hidden field
        UserCode = request.POST.get('UserCode')

        print("DEBUG POST:", request.POST)

        if not booking_id or not action or not OrderId:
            return JsonResponse({"success": False, "message": "Missing parameters"})

        #return JsonResponse({"success": True, "message": "Booking Status updated successfully"})
        try:
            # Build WithdrawlStatus from action
            status_map = {
                "approve": "SUCCESS",
                "reject": "REJECTED",
                "delivered": "CANCELED"   # if you add delivery action later
            }
            booking_status = status_map.get(action.lower(), "PENDING")
            print(booking_status)

            # API endpoint
            api_url = "https://www.gyaagl.app/goldvault_api/bookingorder"

            # Payload
            payload = {
                "UserCode": UserCode,
                "BookingId": booking_id,
                "OrderStatus": booking_status,
                "OrderId":OrderId,
                # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
                "ClientCode": client_code,
            }

            headers = {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Origin": "https://www.gyaagl.app",
                "Referer": "https://www.gyaagl.app/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            # Make request
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            print(response.text)
            # response_text = response.text.strip()
            # first_brace = response_text.find("{")
            # last_brace = response_text.rfind("}")
            # clean_json = response_text[first_brace:last_brace+1] if first_brace != -1 else "{}"
            # data = json.loads(clean_json)
            data=response.json()
            booking_status= booking_status if booking_status !='SUCCESS' else "APPROVED"
            if response.status_code == 200 and data.get("message_code") == 1000:
                return JsonResponse({"success": True, "message": f"{booking_status} successfully"})
                # return JsonResponse({"success": True, "message": "Status updated successfully"})
            else:
                return JsonResponse({
                    "success": False,
                    "message": data.get("message_text", f"API error {response.status_code}")
                })

        except Exception as e:
            return JsonResponse({"success": False, "message": f"API Exception: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request"})

#################################### Get Withdraw List ############################################
@owner_required
def get_withdrawal_list(request):
    date = request.GET.get('date')
    print("844",date)
    if not date :
        # today = datetime.today()
        # # Format for API (dd/mm/YYYY)
        # date_str = today.strftime("%d/%m/%Y")
        # # Format for input field (YYYY-mm-dd)
        # date = today.strftime("%Y-%m-%d")
        # date_str = "22/08/2025"
        # Get IST timezone
        ist = pytz.timezone("Asia/Kolkata")
        # Current time in IST
        today = datetime.now(ist)
        # Format for API (dd/mm/YYYY)
        date_str = today.strftime("%d/%m/%Y")
        date = today.strftime("%Y-%m-%d")
        print("today's date",date_str)
    
    else:
        date_str = date # example: "2025-08-24"
        if date_str:  
            try:
                y, m, d = date_str.split('-')   # "2025", "08", "24"
                date_str = f"{d}/{m}/{y}"       # "24/08/2025"
            except ValueError:
                # if format is not correct, keep as is
                pass
    
    print("863",date)
    print("864",date_str)
    Withdrawal = {}
    error = None
    client_code = request.session.get('ClientCode', None)

    api_url = "https://www.gyaagl.app/goldvault_api/gettranwithdrawal"
    payload = {
        # "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
        "ClientCode": client_code,
        "TransactionDate":date_str
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        # print("DEBUG: Withdrawal API response:", response.text)
        data = response.json()
        if data.get("message_code") == 1000:
            # data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                Withdrawal_data = data["message_data"]   # ✅ store booking list in Withdrawal
                Withdrawal= Withdrawal_data.get('Withdrawal', {})
                # print("1020",Withdrawal)
            else:
                error = data.get("message_text", "No Withdrwals found.")
        else:
            error = f"{data.get("message_text")}"

    except Exception as e:
        error = f"Withdrawal API Exception: {str(e)}"
        print(error)

    print(Withdrawal)
    return render(
        request,
        "owner/getall_withdrawal_list.html",
        {"Withdrawal": Withdrawal,'date':date ,"error": error,},
    )

############################################ Member Booking List #######################################################
@owner_required
def member_booking_list(request):
    members = []
    error = None

    api_url = "https://www.gyaagl.app/goldvault_api/getorders" #booking orders
    client_code = request.session.get('ClientCode', None)
    payload = {
        "ClientCode":client_code
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        #print("DEBUG: Booking order API response:", response.text)

        
        data = response.json()

        if data.get("message_code") == 1000:
            # data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                members = data["message_data"]   # ✅ store booking order list in members
            else:
                error = data.get("message_text", "No Bookings order found.")
        else:
            error = f"{data.get("message_text")}"

    except Exception as e:
        error = f"booking order API Exception: {str(e)}"
        print(error)

    # for m in members:
    #     m['OrderStatus']='3'
    #     print(m)
    return render(
        request,
        "owner/member_booking_list.html",
        {"members": members, "error": error},
    )
    
    
########################################################################################
#######################QR PDF###################################
def convert_pdf_to_images(pdf_path, output_folder,contact_number=1):
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x for quality
        image_path = os.path.join(output_folder, f"{contact_number}{page_num + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    return image_paths


# @user_required
# def owner_qr(request):
#     # Paths
#     # pdf_name = "goldvaultQR.pdf"
#     pdf_name = "shop1.pdf"
#     pdf_path = os.path.join(settings.BASE_DIR, "static", "assets", "img", "QRPDF", pdf_name)
#     img_dir = os.path.join(settings.BASE_DIR, "static", "assets", "img", "QRImage")

#     # Ensure folder exists
#     os.makedirs(img_dir, exist_ok=True)

#     try:
#         # Convert all PDF pages to images
#         image_paths = convert_pdf_to_images(pdf_path, img_dir)
#     except Exception as e:
#         return render(request, "owner/owner_qr.html", {"error": f"PDF conversion failed: {str(e)}"})

#     # Get static URLs for generated images
#     image_urls = [f"assets/img/QRImage/{os.path.basename(path)}" for path in image_paths]

#     return render(request, "owner/owner_qr.html", {
#         "image_urls": image_urls,
#         "pdf_url": f"assets/img/QRPDF/{pdf_name}",
#     })

@user_required
def owner_qr(request):
    client_code = request.session.get('ClientCode', None)
    contact_number = request.session.get("user").get('UserMobileNo')  # must be stored in session earlier
    print(client_code,contact_number)
    if not client_code or not contact_number:
        return render(request, "owner/owner_qr.html", {"error": "Client Code or Contact Number missing"})

    pdf_dir = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "QRPDF")
    img_dir = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "QRImage")
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    pdf_path = os.path.join(pdf_dir, f"{contact_number}.pdf")
    img_path = os.path.join(img_dir, f"{contact_number}1.png")

    # --- CASE 1: Image already exists ---
    if os.path.exists(img_path):
        print("CASE 1: Image already exists")
        image_urls = [f"assets/img/QRImage/{os.path.basename(img_path)}"]
        return render(request, "owner/owner_qr.html", {"image_urls": image_urls,"pdf_url": f"assets/img/QRPDF/{contact_number}.pdf"})

    # --- CASE 2: Image not present but PDF exists → convert ---
    if os.path.exists(pdf_path):
        print("CASE 2: Image not present but PDF exists → convert ")
        try:
            image_paths = convert_pdf_to_images(pdf_path, img_dir,contact_number)
            image_urls = [f"assets/img/QRImage/{os.path.basename(p)}" for p in image_paths]
            return render(request, "owner/owner_qr.html", {"image_urls": image_urls,"pdf_url": f"assets/img/QRPDF/{contact_number}.pdf"})
        except Exception as e:
            return render(request, "owner/owner_qr.html", {"error": f"PDF conversion failed: {str(e)}"})

    # --- CASE 3: Neither exists → generate PDF then convert ---
    try:
        print("CASE 3: Neither exists → generate PDF then convert")
        create_shop_qr_pdf(client_code, contact_number)  # save PDF
        image_paths = convert_pdf_to_images(pdf_path, img_dir ,contact_number)
        image_urls = [f"assets/img/QRImage/{os.path.basename(p)}" for p in image_paths]
        return render(request, "owner/owner_qr.html", {"image_urls": image_urls,"pdf_url": f"assets/img/QRPDF/{contact_number}.pdf"})
    except Exception as e:
        return render(request, "owner/owner_qr.html", {"error": f"Failed to generate QR PDF: {str(e)}"})



def create_shop_qr_pdf(client_code, contact_number):
    """
    Generate Shop QR PDF for given client_code & contact_number.
    Save as contact_number.pdf in static/assets/img/QRPDF.
    Return path to generated PDF.
    """
    print(client_code,contact_number)
    # API call to fetch client details
    api_url = "https://www.gyaagl.app/goldvault_api/clientinfo"
    payload = {"ClientCode": client_code}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    client_data = None
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        print(response.text)
        data = response.json()
        if data.get("message_code") == 1000 and data.get("message_data"):
            client_data = data["message_data"][0]
    except Exception as e:
        raise Exception(f"Client API error: {str(e)}")

    print(client_data)
    # Fallback if no client data
    business_name = client_data.get('BusinessName', 'Gold Jewellery')
    business_address = client_data.get('BusinessAddress', 'Pune')
    owner_name = client_data.get('OwnerName', 'Unknown')
    contact_number = client_data.get('OwnerContact', contact_number)

    qr_url = f"https://gyaagl.club/GoldVault/?ClientCode={client_code}"

    # Template path
    template_path = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "QRPDF", "ShopQR2.pdf")
    existing_pdf = PdfReader(open(template_path, "rb"))
    output = PdfWriter()

    # Create overlay
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)

    # Logo
    # logo_path = os.path.join(settings.BASE_DIR, "static", "assets", "img", "icon", "512x512.png")
    # try:
    #     can.drawImage(ImageReader(logo_path), 65, 680, width=100, height=100, preserveAspectRatio=True, mask="auto")
    # except:
    #     pass

    # --- Logo Selection Logic ---
    logo_dir = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "company_logo")
    logo_path_contact = os.path.join(logo_dir, f"{contact_number}.png")
    default_logo_path = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "icon", "512x512.png")

    if os.path.exists(logo_path_contact):
        logo_path = logo_path_contact
    elif os.path.exists(default_logo_path):
        logo_path = default_logo_path
    else:
        logo_path = None  # no logo available

    # --- Draw Logo if available ---
    if logo_path:
        try:
            can.drawImage(ImageReader(logo_path), 65, 680, width=100, height=100, preserveAspectRatio=True, mask="auto")
        except Exception as e:
            print(f"Logo drawing failed: {e}")


    # Business details
    can.setFont("Helvetica-Bold", 16)
    can.drawCentredString(370, 770, business_name)
    can.setFont("Helvetica", 14)
    can.drawCentredString(370, 750, business_address)
    can.drawCentredString(370, 730, owner_name)
    can.drawCentredString(370, 710, contact_number)

    # QR code
    qr_img = qrcode.make(qr_url)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    can.drawImage(ImageReader(qr_buffer), 200, 357, width=200, height=200, preserveAspectRatio=True, mask="auto")

    can.save()
    packet.seek(0)

    # Merge
    overlay_pdf = PdfReader(packet)
    page = existing_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    output.add_page(page)

    # Save to file
    pdf_dir = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "QRPDF")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"{contact_number}.pdf")

    with open(pdf_path, "wb") as f:
        output.write(f)

    return pdf_path

##################to genrate pdf and see on browser###############
def generate_shop_qr_pdf(request,ClientCode):
    print("ClientCode",ClientCode)
    # --- Demo Data (replace dynamically later) ---
    business_name = "Demo Shop Pvt Ltd"
    business_address = "123 Market Street, Pune, India"
    owner_name = "John Doe"
    contact_number = "9876543210"
    # client_code = "675c347d-83d1-11f0-9769-525400ce20fd"
    client_code = ClientCode
    qr_url = f"https://gyaagl.club/GoldVault/?ClientCode={client_code}"

    if not ClientCode :
        return JsonResponse({"success": False, "message": "Client Code Missing"})

    api_url = "https://www.gyaagl.app/goldvault_api/clientinfo"
    payload = {
        "ClientCode": client_code
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        error = None
        client_data=None
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        print("DEBUG: Client Details API response:", response.text)
        data = response.json()
        if data.get("message_code") == 1000:
            # data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                client_data = data["message_data"][0]   # ✅ store booking list in bookings
            else:
                error = data.get("message_text", "No Client Data found.")
        else:
            error = f"{data.get("message_text")}"

    except Exception as e:
        error = f"Client Details API Exception: {str(e)}"
        print(error)

    if not client_data:
        print(client_data)
        return JsonResponse({"success": False, "message": error})
    
    
    print(client_data)
    business_name = client_data.get('BusinessName','Gold Jewellery')
    business_address = client_data.get('BusinessAddress','Pune')
    owner_name = client_data.get('OwnerName','Unknown')
    contact_number = client_data.get('OwnerContact','1234567890')
    
    # --- Load Template (⚠️ don't close file) ---
    template_path = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "QRPDF", "ShopQR2.pdf")
    existing_pdf = PdfReader(open(template_path, "rb"))   # ✅ same as your authorization logic
    output = PdfWriter()

    # --- Create Overlay ---
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)

    # Insert Shop Logo (top-left block)
    # logo_path = os.path.join(settings.BASE_DIR, "static", "assets", "img","icon", "512x512.png")
    # try:
    #     can.drawImage(ImageReader(logo_path), 65, 680, width=100, height=100, preserveAspectRatio=True, mask="auto")
    # except:
    #     pass

    # --- Logo Selection Logic ---
    logo_dir = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "company_logo")
    logo_path_contact = os.path.join(logo_dir, f"{contact_number}.png")
    default_logo_path = os.path.join(settings.BASE_DIR, "static", "assets", "img", "icon", "512x512.png")

    if os.path.exists(logo_path_contact):
        logo_path = logo_path_contact
    elif os.path.exists(default_logo_path):
        logo_path = default_logo_path
    else:
        logo_path = None  # no logo available

    # --- Draw Logo if available ---
    if logo_path:
        try:
            can.drawImage(ImageReader(logo_path), 65, 680, width=100, height=100, preserveAspectRatio=True, mask="auto")
        except Exception as e:
            print(f"Logo drawing failed: {e}")


    # Business details beside logo
    can.setFont("Helvetica-Bold", 16)
    can.drawCentredString(370, 770, business_name)

    can.setFont("Helvetica", 14)
    can.drawCentredString(370, 750, business_address)
    can.drawCentredString(370, 730, owner_name)
    can.drawCentredString(370, 710, contact_number)

    # QR Code in center
    qr_img = qrcode.make(qr_url)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    can.drawImage(ImageReader(qr_buffer), 200, 357, width=200, height=200, preserveAspectRatio=True, mask="auto")

    can.save()
    packet.seek(0)

    # --- Merge Overlay with Template ---
    overlay_pdf = PdfReader(packet)
    page = existing_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    output.add_page(page)

    # --- Save Final PDF ---
    final_pdf = io.BytesIO()
    output.write(final_pdf)
    final_pdf.seek(0)

    # --- Return File ---
    return FileResponse(final_pdf, content_type="application/pdf")


############Regenerate the QR PDF for Owner

def regenerate_qr_pdf_and_image(client_code, contact_number=None):
    if not client_code:
        return {"success": False, "message": "Client Code is required"}

    # --- Step 1: Call API to fetch client info ---
    api_url = "https://www.gyaagl.app/goldvault_api/clientinfo"
    payload = {"ClientCode": client_code}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        data = response.json()
        if data.get("message_code") != 1000 or not data.get("message_data"):
            return {"success": False, "message": "Client data not found"}
        client_data = data["message_data"][0]
    except Exception as e:
        return {"success": False, "message": f"Client API error: {str(e)}"}

    # --- Step 2: Extract API contact ---
    api_contact = client_data.get("OwnerContact")
    if not api_contact:
        return {"success": False, "message": "API did not return contact number"}

    # --- Step 3: Handle contact number mismatch ---
    pdf_dir = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "QRPDF")
    img_dir = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "QRImage")
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    if contact_number and contact_number != api_contact:
        # delete old files with passed contact number
        old_pdf = os.path.join(pdf_dir, f"{contact_number}.pdf")
        old_img = os.path.join(img_dir, f"{contact_number}1.png")
        for f in [old_pdf, old_img]:
            if os.path.exists(f):
                os.remove(f)
        # replace with api contact
        contact_number = api_contact
    else:
        contact_number = api_contact

    # --- Step 4: Generate PDF using existing function ---
    try:
        pdf_path = create_shop_qr_pdf(client_code, contact_number)
    except Exception as e:
        return {"success": False, "message": f"PDF generation failed: {str(e)}"}

    # --- Step 5: Convert PDF → Image using existing function ---
    try:
        convert_pdf_to_images(pdf_path, img_dir, contact_number)
    except Exception as e:
        return {"success": False, "message": f"Image generation failed: {str(e)}"}

    return {"success": True, "message": "Successfully regenerated PDF and images"}


#### get request to regenerate pdf and image
@owner_required
def regenerate_pdf(request):
    if(request.method=='GET'):
        client_code = request.session.get('ClientCode', None)
        contact_number = request.session.get("user").get('UserMobileNo')

        if not client_code or not contact_number:
           messages.info(request,"Client Code or Contact Number missing")
           return redirect('owner_qr') 

        result = regenerate_qr_pdf_and_image(client_code,contact_number)
        print(result)
        if(result and result.get('success',False)):
            messages.success(request,"Successfully Regenerated PDF")
        
        else:
            message = result.get('message',"Some Unwanted Problem occur please contact to Support Team")
            messages.info(request,message)
       
        return redirect('owner_qr')

################################### Update Profile ############################################
@user_required
def update_profile(request):
    session_user = request.session.get("user", {})
    client_code = request.session.get("ClientCode")

    user_data = session_user or {}
     # Convert epoch to yyyy-mm-dd for input field
    user_dob_epoch = session_user.get("UserDOB")
    user_dob_formatted = ""

    if user_dob_epoch:
        try:
            dt = datetime.fromtimestamp(int(user_dob_epoch))
            user_dob_formatted = dt.strftime("%Y-%m-%d")  # format for <input type="date">
        except Exception:
            pass

    # Replace in session copy for template
    session_user["UserDOB"] = user_dob_formatted

    if request.method == "POST":
        # Convert DOB from dd/mm/yyyy to epoch
        dob_input = request.POST.get("UserDOB") or ""
        formatted_dob = ""

        if dob_input:
            try:
                dt = datetime.strptime(dob_input, "%Y-%m-%d")
                formatted_dob = dt.strftime("%d/%m/%Y")
            except ValueError:
                formatted_dob = dob_input  # fallback if parsing fails

        print(formatted_dob)  # e.g., 18/12/1979

        # Collect form data
        updated_data = {
            "ClientCode": client_code,
            "UserCode": session_user.get("UserCode"),
            "UserFullName": request.POST.get("UserFullName"),
            "UserPANNo": request.POST.get("UserPANNo") or "",
            "UserAadharNo": request.POST.get("UserAadharNo") or "",
            "UserGender": request.POST.get("UserGender") or "",  # should be "1"/"2"/"3"
            "UserDOB": formatted_dob,
        }

        print("=== Update Profile Data ===")
        for k, v in updated_data.items():
            print(f"{k}: {v}")

        try:
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://www.gyaagl.app",
                "Referer": "https://www.gyaagl.app/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            }

            api_url = "https://www.gyaagl.app/goldvault_api/updateprofile"
            response = requests.post(api_url, json=updated_data, headers=headers, timeout=10)
            print("API RESPONSE ===", response.text)

            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("message_code") == 1000:
                    if res_json.get("message_data"):
                        updated_user = res_json["message_data"][0]
                        request.session["user"] = updated_user

                    messages.success(request, res_json.get("message_text", "Profile updated successfully ✅"))
                else:
                    messages.error(request, res_json.get("message_text", "Failed to update profile"))
            else:
                messages.error(request, f"API Error: {response.status_code}")

        except Exception as e:
            messages.error(request, f"Error while updating profile: {str(e)}")

        return redirect("update_profile")

    return render(request, "update_profile.html", {"user": user_data})

################################### Profile Picture ############################################
@user_required
@csrf_exempt
def update_profile_pic(request):
    user = request.session.get("user", {})
    client_code = request.session.get("ClientCode", None)

    if request.method == "POST":
        user_code = user.get("UserCode")
        client_code = request.session.get("ClientCode")

        # Uploaded file
        uploaded_file = request.FILES.get("UserProfilePhotoURL")

        print("=== Profile Pic Update ===")
        print("ClientCode:", client_code)
        print("UserCode:", user_code)
        print("Uploaded File:", uploaded_file)

        if uploaded_file:
            # ==============================
            # 1) Save image in static folder
            # ==============================
            img_directory = os.path.join(settings.BASE_DIR, 'staticfiles', 'assets', 'profile_pic')
            os.makedirs(img_directory, exist_ok=True)

            # Always save as PNG with user code as filename (overwrite mode)
            file_name = f"{user_code}.png"
            file_path = os.path.join(img_directory, file_name)

            # Convert and save as PNG
            image = Image.open(uploaded_file)
            image = image.convert("RGBA")
            image.save(file_path, "PNG")

            # Public URL (adjust domain/path if needed)
            profile_photo_url = f"https://gyaagl.club/GoldVault/static/assets/profile_pic/{file_name}"

            print("Saved Image Path:", file_path)
            print("Public URL:", profile_photo_url)

            # ==============================
            # 2) Call API with URL
            # ==============================
            api_url = "https://www.gyaagl.app/goldvault_api/userphoto"

            headers = {
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://www.gyaagl.app",
                "Referer": "https://www.gyaagl.app/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            }

            data = {
                "ClientCode": client_code,
                "UserCode": user_code,
                "UserProfilePhotoURL": profile_photo_url,
            }

            try:
                response = requests.post(api_url, headers=headers, json=data)
                print("Raw Response:", response.text)

                response_data = response.json()
                print("API Response:", response_data)

                if response_data.get("message_code") == 1000:
                    messages.success(request, response_data.get("message_text", "Profile picture updated successfully!"))
                else:
                    messages.error(request, response_data.get("message_text", "Failed to update profile picture."))

            except Exception as e:
                print("Error calling API:", e)
                messages.error(request, "Something went wrong while updating profile picture.")
        else:
            messages.error(request, "Please upload a valid image.")

        return redirect("update_profile_pic")

    return render(request, "update_profile_pic.html", {
        "user": user,
        "ClientCode": client_code,
    })
    
############################################# Update Client Profile ################################################    
@user_required
def update_client_details(request):
    client_code = request.session.get("ClientCode", None)
    client_data = None  

    # API to fetch client info (for pre-fill)
    client_info_url = "https://www.gyaagl.app/goldvault_api/clientinfo"
    payload = {"ClientCode": client_code}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(client_info_url, json=payload, headers=headers, timeout=10)
        data = response.json()
        if data.get("message_code") == 1000 and data.get("message_data"):
            client_data = data["message_data"][0]
    except Exception as e:
        print(f"Client API error: {str(e)}")

    # handle form submit
    if request.method == "POST":
        try:
            print("=== Client Details Submitted ===")

            # prepare payload for API (ClientCode compulsory, rest optional)
            submitted_data = {
                "ClientCode": client_code,
                "BusinessName": request.POST.get("BusinessName") or None,
                "OwnerName": request.POST.get("OwnerName") or None,
                "OwnerContact": request.POST.get("OwnerContact") or None,
                "LoginPin": request.POST.get("LoginPin") or None,
                "BusinessAddress": request.POST.get("BusinessAddress") or None,
                "BusinessCityId": request.POST.get("BusinessCityId") or None,
                "BusinessStateId": request.POST.get("BusinessStateId") or None,
                "OwnerEmail": request.POST.get("OwnerEmail") or None,
                "ShopPhotoURL": request.POST.get("ShopPhotoURL") or None,
            }

            # print all fields (debugging)
            for key, value in submitted_data.items():
                print(f"{key}: {value}")

            # send to API
            client_profile_url = "https://www.gyaagl.app/goldvault_api/clientprofile"
            api_response = requests.post(client_profile_url, json=submitted_data, headers=headers, timeout=10)
            api_data = api_response.json()

            print("=== API Response ===", api_data)

            if api_data.get("message_code") == 1000:
                messages.success(request, api_data.get("message_text", "Client details updated successfully."))
                # refresh local client_data for rendering updated values
                if client_data:
                    client_data.update({k: v for k, v in submitted_data.items() if v})
            else:
                messages.error(request, api_data.get("message_text", "Failed to update client details."))

        except Exception as e:
            print(f"Error in client details update: {e}")
            messages.error(request, "Something went wrong while updating details.")

    return render(request, "owner/update_client_details.html", {
        "client_data": client_data
    })

############################################# Update Bank Details ################################################    
@user_required
def update_bank_details(request):
    client_code = request.session.get("ClientCode", None)
    user = request.session.get("user", {})
    client_data = None  

    # API to fetch existing client info
    client_info_url = "https://www.gyaagl.app/goldvault_api/clientinfo"
    payload = {"ClientCode": client_code}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # Fetch existing client info
    try:
        response = requests.post(client_info_url, json=payload, headers=headers, timeout=10)
        data = response.json()
        if data.get("message_code") == 1000 and data.get("message_data"):
            client_data = data["message_data"][0]
    except Exception as e:
        print(f"Client API error: {str(e)}")
        messages.error(request, "Unable to fetch client details. Please try again.")

    # Handle form submission
    if request.method == "POST":
        try:
            # Collect bank details from form
            bank_payload = {
                "ClientCode": client_code,
                "UserCode": user.get("UserCode"),
                "UPIID": request.POST.get("UPIID"),
                "BankAccountName": request.POST.get("BankAccountName"),
                "BankAccountNo": request.POST.get("BankAccountNo"),
                "BankName": request.POST.get("BankName"),
                "BranchName": request.POST.get("BranchName"),
                "IFSCCode": request.POST.get("IFSCCode"),
                "BranchAddress": request.POST.get("BranchAddress"),
            }

            print("=== Sending Bank Details ===")
            for key, value in bank_payload.items():
                print(f"{key}: {value}")

            # API to update client bank details
            client_bank_url = "https://www.gyaagl.app/goldvault_api/clientbank"
            bank_response = requests.post(client_bank_url, json=bank_payload, headers=headers, timeout=10)
            bank_data = bank_response.json()
            print(bank_data)

            if bank_data.get("message_code") == 1000:
                messages.success(request, bank_data.get("message_text", "Bank details updated successfully."))
                
                # update local data for rendering
                if client_data:
                    client_data.update(bank_payload)
            else:
                messages.error(request, bank_data.get("message_text", "Failed to update bank details."))

        except Exception as e:
            print(f"Error updating bank details: {e}")
            messages.error(request, "Something went wrong while updating. Please try again.")

    return render(request, "owner/update_bank_details.html", {
        "client_data": client_data
    })

##################################### Notification ######################################
@user_required
def notification_list(request):
    user_code = request.session.get('user', {}).get('UserCode')
    client_code = request.session.get('ClientCode')
    # user_code = "675c4ad2-83d1-11f0-9769-525400ce20fd"
    # client_code = "675c347d-83d1-11f0-9769-525400ce20fd"

    api_url = "https://www.gyaagl.app/goldvault_api/notification/notificationlist"

    payload = {
        "ClientCode": client_code,
        "UserCode": user_code,
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.gyaagl.app",
        "Referer": "https://www.gyaagl.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    notifications = []
    error = None

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # print(data)

        if data.get("message_code") == 1000 and data.get("message_text"):
            notifications = data["message_text"]   # list of notifications
        else:
            error = data.get("message_text", "No notifications found.")
    except requests.exceptions.RequestException as e:
        error = f"Request error: {e}"
    except Exception as e:
        error = f"Error: {e}"

    return render(request, "notification_list.html", {
        "notifications": notifications,
        "error": error,
    })



@csrf_exempt
def update_all_notifications_read(request):
    if request.method == "POST":
        user_code = request.session.get('user').get('UserCode')
        client_code = request.session.get('ClientCode')
        # user_code = "675c4ad2-83d1-11f0-9769-525400ce20fd"
        # client_code = "675c347d-83d1-11f0-9769-525400ce20fd"

        api_url = "https://www.gyaagl.app/goldvault_api/notification/updateallnotificationread"
        payload = {
            "ClientCode": client_code,
            "UserCode": user_code
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(data)
                if data.get("message_code") == 1000:
                    return JsonResponse({"success": True, "message": "All notifications marked as read"})
                else:
                    return JsonResponse({"success": False, "message": data.get("message_text", "API Error")})
            else:
                return JsonResponse({"success": False, "message": "Failed with status code {}".format(response.status_code)})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method"})

@csrf_exempt
def update_notification_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            # ✅ Get codes from session instead of frontend
            user_data = request.session.get("user", {})
            user_code = user_data.get("UserCode")
            client_code = user_data.get("ClientCode")
  
            # user_code = "675c4ad2-83d1-11f0-9769-525400ce20fd"
            # client_code = "675c347d-83d1-11f0-9769-525400ce20fd"

            payload = {
                "ClientCode": client_code,
                "UserCode": user_code,
                "Notification_Id": data.get("Notification_Id")
            }
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            print("Payload to API:", payload)

            # Call external API
            url = "https://www.gyaagl.app/goldvault_api/notification/statusupdate"
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            api_response = response.json()
            print("API Response:", api_response)

            if api_response.get("message_code") == 1000:
                return JsonResponse({"success": True, "message": "Notification read successfully"})
            else:
                return JsonResponse({"success": False, "message": api_response.get("message_text", "Failed to update")})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"})
