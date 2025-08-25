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
                print(data)
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

def dashboard_view(request):
    # user_code = request.COOKIES.get("user_code")
    user_code = request.session.get('user').get('UserCode')
    print(user_code)
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

    return render(request, "dashboard.html", {
        "stats": stats,
        "user": user,
        "sell_rate": sell_rate
    })
    # return render(request, "dashboard.html", {"stats": stats, "user": user})


# def dashboard1_view(request):
#     user_code = request.session.get('user').get('UserCode')
#     print(user_code)
#     # user_code = request.COOKIES.get("user_code")
#     # print("DEBUG: UserCode from cookie =>", user_code)

#     api_url = "https://www.gyaagl.app/goldvault_api/getbalances"
#     payload = {
#         "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
#         "UserCode": "14e2b5b6-7cb8-11f0-9769-525400ce20fd"
#     }
#     headers = {
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#     }

#     stats = {"current_balance": 0, "total_value": 0, "total_invested": 0, "gain_loss": 0}

#     try:
#         response = requests.post(api_url, json=payload, headers=headers, timeout=10)
#         print("DEBUG: Balance API response:", response.text)

#         if response.status_code == 200:
#             data = response.json()
#             if data.get("message_code") == 1000 and data.get("message_data"):
#                 booking_list = data["message_data"].get("BookingId", [])
#                 if booking_list:
#                     booking = booking_list[0]
#                     stats["current_balance"] = booking.get("Balance", 0)
#                     stats["product_weight"] = booking.get("ProductWeight", 0)
#                     stats["total_invested"] = booking.get("AmountInvested", 0)
#                     stats["gain_loss"] = booking.get("GainLoss", 0)
#                     stats["total_withdrwal"] = booking.get("AmountWithdrawl", 0)
#                     stats["withdrawl_weight"] = booking.get("WithdrawlWeight", 0)

#                 else:
#                     print("BookingId list is empty")
#             else:
#                 print("API returned empty message_data or error:", data.get("message_text"))
#         else:
#             print("HTTP error:", response.status_code)
#     except Exception as e:
#         print("Dashboard1 API Exception:", e)
#     rate_api_url = "https://www.gyaagl.app/goldvault_api/getrate"
#     rate_payload = {
#         "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
#     }
#     try:
#         rate_response = requests.post(rate_api_url, json=rate_payload, headers=headers, timeout=10)
#         print("DEBUG: Rate API response:", rate_response.text)

#         if rate_response.status_code == 200:
#             rate_data = rate_response.json()
#             if rate_data.get("message_code") == 1000 and rate_data.get("message_data"):
#                 sell_rate = rate_data["message_data"][0].get("SellRate")
#     except Exception as e:
#         print("Dashboard Rate API Exception:", e)

#     return render(request, "dashboard1.html", {
#         "stats": stats,
#         "sell_rate": sell_rate
#     })


def dashboard1_view(request):
    user_code = request.session.get('user').get('UserCode')
    # print(user_code)

    api_url = "https://www.gyaagl.app/goldvault_api/getbalances"
    payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
        "UserCode": user_code
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
    rate_payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7"}

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
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",
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

    return render(request, "dashboard1.html", {
        "stats": stats,
        "sell_rate": sell_rate,
        "transactions": transactions
    })
    
########################################### Get Transection List ##################################################
def get_transection_list(request):
    user_code = request.session.get('user').get('UserCode')
    print("DEBUG: UserCode =>", user_code)

    transactions = []
    error = None

    transactions_api_url = "https://www.gyaagl.app/goldvault_api/gettransactions"
    trans_payload = {
        "ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7",  # keep fixed if API requires
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
def details_transection(request, id):
    user_code = request.session.get('user').get('UserCode')
    client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"

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
            error = f"API Error: {response.status_code}"

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
    client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"

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

        user = request.session.get('user', {})
        user_code = user.get('UserCode')
        client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"

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
            "BookingWeight": weight,
            "UserCode": user_code
        }

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
        client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
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
    request.session.flush()  
    return redirect('login')
########################################### Change Pin ##############################################
def change_pin(request): 
    user_code = request.session.get('user').get('UserCode')
    client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"

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

    return render(request, "user/change_pin.html")


######################################## Update Nominee ########################################
def update_nominee(request): 
    client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
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

    return render(request, "user/update_nominee.html", {"nominees": nominee_data})
############################################# Send Money ####################################################
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
def faq(request):
    user_code = request.session.get('user', {}).get('UserCode')
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"

    payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "2"}
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
def termsofuse(request):
    user_code = request.session.get('user', {}).get('UserCode')
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"

    payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "1"}
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
def privacypolicy(request):
    user_code = request.session.get('user', {}).get('UserCode')
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"

    payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "3"}
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
def membershipagrement(request):
    user_code = request.session.get('user', {}).get('UserCode')
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"

    payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "4"}
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
def support_contact(request):
    user_code = request.session.get('user', {}).get('UserCode')
    api_url = "https://www.gyaagl.app/goldvault_api/getsupporttext"

    payload = {"ClientCode": "5dc0abf7-85de-4ede-abff-e7d53e3804b7", "TextType": "5"}
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
def old_queries(request):
    user = request.session.get('user', {})
    user_code = user.get('UserCode')
    user_name = user.get('UserFullName')   # ✅ fetch name
    client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"
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
def raise_query(request):
    user_code = request.session.get('user', {}).get('UserCode')
    client_code = "5dc0abf7-85de-4ede-abff-e7d53e3804b7"

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
        # user_code = "14e2b5b6-7cb8-11f0-9769-525400ce20fd"
        user_code = request.session.get('user', {}).get('UserCode')

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
        return render(request, "member_list.html", {"members": members})

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
