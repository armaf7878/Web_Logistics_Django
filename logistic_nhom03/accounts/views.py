from logistic_nhom03 import settings
from django.shortcuts import render ,redirect
from django.contrib import messages
from firebase_admin import auth, firestore
from django.http import JsonResponse
import requests
import json
db = settings.firestore_db
FIREBASE_API_KEY = "AIzaSyCgf2cpIwqhkNh0k6OBhFGDLlPGQH2Qee0"
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        role = request.POST.get('role', 'staff')

        try:
            user = auth.create_user(
                email = email,
                password = password,
                display_name = name
            )
            db.collection('users').document(user.uid).set({
                'name': name,
                'email': email,
                'phone': phone,
                'role': role,
                'active': True,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            messages.success(request, 'Tạo tài khoản thành công')

            return redirect('login')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            payload = json.dumps({
                "email": email,
                "password": password,
                "returnSecureToken": True
            })
            
            res = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}",
                data=payload
            )
            data = res.json()
            if 'idToken' in data:
                request.session['firebase_user'] = data
                messages.success(request, 'Đăng nhập thành công!')
                user_id = request.session['firebase_user'].get('localId')
                print(user_id)
                role = db.collection('users').document(user_id).get().to_dict().get('role')
                
                if(role == 'staff'):
                    return redirect('dashboard')
                print(role)
                if(role == 'deliver'):  
                    return redirect('deliver')
                
            else:
                messages.error(request, 'Sai email hoặc mật khẩu.')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'accounts/login.html')

def logout_view(request):
    if 'firebase_user' in request.session:
        del request.session['firebase_user']
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('login')
    