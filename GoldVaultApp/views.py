from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from django.http import JsonResponse
import json
from urllib.parse import urlencode

def BASE(request):
    return render(request, 'base.html')

def forgot_password(request):
    return render(request, "forgot_password.html")

def register(request):
    return render(request, "register.html")
def setting(request):
    return render(request, "setting.html")
from django.shortcuts import render, redirect
import requests



def login_view(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        pin = request.POST.get('pin_number')
        api_url = 'https://www.gyaagl.app/goldvault_api/login'
        payload = {
            "UserMobileNo": mobile,
            "UserPin": pin,
            "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
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
                if data.get("message_code") == 1000:
                    user = data["message_data"][0]
                    user_status = int(user.get("UserStatus", -1))
                    user_code = user.get("UserCode")

                    context = {
                        "user": user
                    }

                if user_status == 1:
                    resp = redirect("dashboard/")  
                    resp.set_cookie("user_code", user_code)
                    return resp
                elif user_status == 0:
                    resp = redirect("dashboard1/")
                    resp.set_cookie("user_code", user_code)
                    return resp
        except Exception as e:
            print("Login Exception:", e)

    return render(request, "base.html")

def dashboard_view(request):
    user_code = request.COOKIES.get("user_code")
    print("DEBUG: UserCode from cookie =>", user_code)

    api_url = "https://www.gyaagl.app/goldvault_api/getbalances"
    payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
        "UserCode": user_code
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    stats = {"current_balance": 0, "total_value": 0, "total_invested": 0, "gain_loss": 0}
    user = {"UserFullName": "", "UserMobileNo": ""}

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        print("DEBUG: Balance API response:", response.text)

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

                user_info = data["message_data"].get("UserDetails", {})
                user["UserFullName"] = user_info.get("UserFullName", "")
                user["UserMobileNo"] = user_info.get("UserMobileNo", "")

            else:
                print("API returned empty message_data or error:", data.get("message_text"))
        else:
            print("HTTP error:", response.status_code)
    except Exception as e:
        print("Dashboard1 API Exception:", e)

    return render(request, "dashboard.html", {"stats": stats, "user": user})


def dashboard1_view(request):
    user_code = request.COOKIES.get("user_code")
    print("DEBUG: UserCode from cookie =>", user_code)

    api_url = "https://www.gyaagl.app/goldvault_api/getbalances"
    payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
        "UserCode": user_code
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    stats = {"current_balance": 0, "total_value": 0, "total_invested": 0, "gain_loss": 0}

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        print("DEBUG: Balance API response:", response.text)

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

                else:
                    print("BookingId list is empty")
            else:
                print("API returned empty message_data or error:", data.get("message_text"))
        else:
            print("HTTP error:", response.status_code)
    except Exception as e:
        print("Dashboard1 API Exception:", e)

    return render(request, "dashboard1.html", {"stats": stats})

def logout_view(request):
    request.session.flush()  
    return redirect('login')

def register(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile_number')
        pin = request.POST.get('pin_number')
        name = request.POST.get('full_name')
        api_url = 'https://www.gyaagl.app/goldvault_api/register'
        payload = {
            "UserMobileNo": mobile,
            "UserPin": pin,
            "FullName": name,
            "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
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
                    return render(request, "base.html", {"user": user})
                else:
                    print("Login failed:", data.get("message_text"))

        except Exception as e:
            print("Exception:", e)

    return render(request, "register.html")

def update_sell_rate(request):
    if request.method == 'POST':
        sell_rate = request.POST.get('sell_rate')
        api_url = 'https://www.gyaagl.app/goldvault_api/dailyrate'  

        payload = {
            "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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
                    return render(request, "dashboard.html", {"sell_rate": sell_rate, "data": data})
                else:
                    return render(request, "dashboard.html", {"error": data.get("message_text")})
            else:
                return render(request, "dashboard.html", {"error": f"HTTP {response.status_code}"})

        except Exception as e:
            print("Exception:", e)
            return render(request, "dashboard.html", {"error": str(e)})

    return render(request, "dashboard.html")


def booking(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        weight = request.POST.get('weight')
        product_daily_rate = request.POST.get('product_daily_rate', '9807')
        user_code = "14e2b5b6-7cb8-11f0-9769-525400ce20fd"

        api_url = 'https://www.gyaagl.app/goldvault_api/booking'
        payload = {
            "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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

def get_balance(request):
    user_code = request.COOKIES.get("user_code")
    api_url = "https://www.gyaagl.app/goldvault_api/getbalances"

    payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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

def send_money(request):
    if request.method == 'POST':
        user_code = request.COOKIES.get("user_code")
        withdraw_amount = request.POST.get('withdraw_amount')
        withdraw_weight = request.POST.get('withdraw_weight')        
        api_url = 'https://www.gyaagl.app/goldvault_api/withdrawlrequest'  

        payload = {
            "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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
                if data.get("message_code") == 1000:
                    return render(request, "dashboard1.html")
                else:
                    return render(request, "dashboard1.html", {"error": data.get("message_text")})
            else:
                return render(request, "dashboard1.html", {"error": f"HTTP {response.status_code}"})
        except Exception as e:
            print("Exception:", e)
            return render(request, "dashboard1.html", {"error": str(e)})
    return render(request, "dashboard1.html")
def get_transactions(request):
    user_code = request.COOKIES.get("user_code")
    print("USERCODE:", user_code)
    api_url = "https://www.gyaagl.app/goldvault_api/gettransactions"  # <-- replace with actual endpoint
    payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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
        raw = response.json()
        transactions = []
        for tx in raw.get("message_data", []): 
            transactions.append({
                "id": tx.get("TransactionId"),
                "status": tx.get("TransactionStatus"),
                "date": tx.get("TransactionDate"),
                "type": tx.get("TransactionType"),
            })
        data = {"transactions": transactions}
    except Exception as e:
        data = {"error": str(e)}
    return JsonResponse(data)
import requests
from django.shortcuts import render
from django.http import JsonResponse

def member_list(request):
    if request.method == "POST":
        api_url = "https://www.gyaagl.app/goldvault_api/getmembers"
        payload = {
            "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
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
                    return JsonResponse({"status": "success", "members": data.get("message_data")})
                else:
                    return JsonResponse({"status": "error", "message": data.get("message_text")})
            else:
                return JsonResponse({"status": "error", "message": f"HTTP {response.status_code}"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return render(request, "dashboard1.html")

def withdrawal_list(request):
    if request.method == "POST":
        api_url = "https://www.gyaagl.app/goldvault_api/getwithdrawls"
        payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"}
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.gyaagl.app",
            "Referer": "https://www.gyaagl.app/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            response_text = response.text.strip()
            first_brace = response_text.find('{')
            last_brace = response_text.rfind('}')
            clean_json = response_text[first_brace:last_brace+1] if first_brace != -1 else '{}'
            try:
                data = json.loads(clean_json)
            except json.JSONDecodeError:
                return JsonResponse({"status": "error", "message": "Invalid JSON from API"})
            if response.status_code == 200 and data.get("message_code") == 1000:
                members = [
                    {
                        "name": m.get("UserFullName"),
                        "mobile": m.get("UserMobileNo"),
                        "product_rate": m.get("ProductDailyRate"),
                        "withdraw_amount": m.get("WithdrawAmount"),
                        "withdraw_weight": m.get("WithdrawWeight")
                    }
                    for m in data.get("message_data", [])
                ]
                return JsonResponse({"status": "success", "members": members})
            else:
                return JsonResponse({"status": "error", "message": data.get("message_text")})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return render(request, "dashboard.html")
