from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from django.http import JsonResponse,HttpResponse
import json
from urllib.parse import urlencode
from functools import wraps
from datetime import datetime
import pytz
from django.views.decorators.csrf import csrf_exempt

##############Decorator to check the user is loggined and it must Owner or not (UserType==1)
def owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.session.get('user')
        if not user or user.get('UserType') != '1':
            request.session.flush()
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

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
                    request.session['user']=user
                    print(user)
                    user_status = int(user.get("UserType", -1))
                    user_code = user.get("UserCode")

                    context = {
                        "user": user
                    }

                if user_status == 1:
                    resp = redirect("dashboard/")  
                    # resp.set_cookie("user_code", user_code)
                    return resp
                elif user_status == 0:
                    resp = redirect("dashboard1/")
                    # resp.set_cookie("user_code", user_code)
                    return resp
        except Exception as e:
            print("Login Exception:", e)

    return render(request, "base.html")

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
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
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
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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

    print(bookings)
    print(withdrawls)
    return render(request, "dashboard.html", {
        # "stats": stats,
        # "user": user,
        "sell_rate": sell_rate,
        "bookings":bookings,
        "withdrawls":withdrawls,
    })
    # return render(request, "dashboard.html", {"stats": stats, "user": user})


def dashboard1_view(request):
    user_code = request.session.get('user').get('UserCode')
    print(user_code)
    # user_code = request.COOKIES.get("user_code")
    # print("DEBUG: UserCode from cookie =>", user_code)

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
    rate_api_url = "https://www.gyaagl.app/goldvault_api/getrate"
    rate_payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
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

    return render(request, "dashboard1.html", {
        "stats": stats,
        "sell_rate": sell_rate
    })
    # return render(request, "dashboard1.html", {"stats": stats})

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

@owner_required
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

def get_rate(request):
    api_url = "https://www.gyaagl.app/goldvault_api/getrate"

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
    # user_code = request.COOKIES.get("user_code")
    user_code = request.session.get('user').get('UserCode')
    print(user_code)
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
        # user_code = request.COOKIES.get("user_code")
        user_code = request.session.get('user').get('UserCode')
        print(user_code)
        
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
    # user_code = request.COOKIES.get("user_code")
    user_code = request.session.get('user').get('UserCode')
    print(user_code)
    
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

@owner_required
def member_list(request):
    api_url = "https://www.gyaagl.app/goldvault_api/getmembers"
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

def withdrawal_list(request):
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


###########Owner-member-transaction list
@owner_required
# def member_transection_list(request,user_code):
def member_transection_list(request):
    if not request.method =='POST':
        return redirect(dashboard_view)
    
    user_code = request.POST['UserCode']
    UserFullName = request.POST['UserFullName']
    UserMobileNo = request.POST['UserMobileNo']
    # UserStatus = request.POST['UserStatus']
    Balance = request.POST['Balance']
    member = {"name":UserFullName,"mobileno":UserMobileNo,"Balance":Balance}

    transactions = []
    error = None

    transactions_api_url = "https://www.gyaagl.app/goldvault_api/gettransactions"
    trans_payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",  # keep fixed if API requires
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
    client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"

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
            error = f"API Error: {response.status_code}"

    except Exception as e:
        error = f"Transactions API Exception: {str(e)}"

    return render(
        request,
        "owner/member_transection_details.html",
        {"transaction": transaction, "error": error, "user_code": user_code},
    )

###########Member-withdrawl-list
@owner_required
def member_withdrawl_list(request):
    members = []
    error = None

    api_url = "https://www.gyaagl.app/goldvault_api/getwithdrawls"
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
                "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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

    api_url = "https://www.gyaagl.app/goldvault_api/getcollection"
    payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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


@csrf_exempt   # remove if you already handle CSRF in template
def update_booking_status(request):
    if request.method == "POST":
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
                "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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

    api_url = "https://www.gyaagl.app/goldvault_api/gettranwithdrawal"
    payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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
        print("DEBUG: Withdrawal API response:", response.text)
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


@owner_required
def member_booking_list(request):
    members = []
    error = None

    api_url = "https://www.gyaagl.app/goldvault_api/getorders" #booking orders
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
        print("DEBUG: Booking order API response:", response.text)

        
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