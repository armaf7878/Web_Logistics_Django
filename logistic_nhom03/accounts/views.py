from logistic_nhom03 import settings
from django.shortcuts import render ,redirect
from django.contrib import messages
from firebase_admin import auth, firestore
from django.http import JsonResponse
import requests
import json
db = settings.firestore_db
FIREBASE_API_KEY = "AIzaSyCgf2cpIwqhkNh0k6OBhFGDLlPGQH2Qee0"

# === BẮT ĐẦU THÊM MỚI: HÀM KIỂM TRA ADMIN ===
# Hàm này kiểm tra user có phải là ADMIN không
def check_role_admin(request):
    try:
        if 'firebase_user' not in request.session:
            return 'login' # Yêu cầu đăng nhập
        
        user_id = request.session['firebase_user'].get('localId')
        user_doc = db.collection('users').document(user_id).get()

        if not user_doc.exists:
            return 'login' # Không tìm thấy user
        
        role = user_doc.to_dict().get('role')

        if role != 'admin':
            return 'dashboard' # Không phải admin, chuyển hướng về dashboard
            
    except Exception as e:
        return 'login' # Lỗi khác thì cứ redirect về login
    
    return None # Là admin, cho phép truy cập
# === KẾT THÚC THÊM MỚI ===


def register(request):
    # === CHỈNH SỬA: GỌI HÀM KIỂM TRA ADMIN ===
    redirect_to = check_role_admin(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'dashboard':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    # === KẾT THÚC CHỈNH SỬA ===

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
            return redirect('showall')
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
                # Xóa thông báo lỗi cũ nếu đăng nhập thành công
                if messages.get_messages(request):
                    list(messages.get_messages(request))

                user_id = request.session['firebase_user'].get('localId')
                print(user_id)
                role = db.collection('users').document(user_id).get().to_dict().get('role')
                print("đã vào đây")
                if(role == 'staff'):
                    print("đã vào đây")
                    return redirect('dashboard')
                print(role)
                if(role == 'deliver'):  
                    return redirect('deliver')
                
                if(role == 'admin'):  
                    return redirect('showall')
                
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


def showall(request):
    # === CHỈNH SỬA: GỌI HÀM KIỂM TRA ADMIN ===
    redirect_to = check_role_admin(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'dashboard':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    # === KẾT THÚC CHỈNH SỬA ===

    user_ref = db.collection('users').get()
    user_list = []
    for user in user_ref:
        item = user.to_dict()
        item['id'] = user.id
        user_list.append(item)
    context = {
        'users': user_list
    }
    return render(request, 'accounts/showall.html', context)

def delete(request, user_id):
    # === BẮT ĐẦU THÊM MỚI: GỌI HÀM KIỂM TRA ADMIN ===
    redirect_to = check_role_admin(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'dashboard':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    # === KẾT THÚC THÊM MỚI ===

    if request.method == 'POST':
        db.collection('users').document(user_id).delete()
        return redirect(showall)
    
def update(request, user_id):
    # === BẮT ĐẦU THÊM MỚI: GỌI HÀM KIỂM TRA ADMIN ===
    redirect_to = check_role_admin(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'dashboard':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    # === KẾT THÚC THÊM MỚI ===

    if request.method == 'POST':
        data = {}
        data['email'] = request.POST.get('email')
        data['phone'] = request.POST.get('phone')
        data['role'] = request.POST.get('role')
        data['active'] = request.POST.get('active') 
        print(data)
        db.collection('users').document(user_id).update(data)
        return redirect(showall)
    user = {}
    doc_ref = db.collection('users').document(user_id).get()
    user = doc_ref.to_dict()
    user['id'] = doc_ref.id
    context = {
        'user': user
    }       
    return render(request, 'accounts/update.html', context)