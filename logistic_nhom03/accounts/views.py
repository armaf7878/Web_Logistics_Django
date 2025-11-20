from logistic_nhom03 import settings
from django.shortcuts import render ,redirect
from django.contrib import messages
from firebase_admin import auth, firestore
from django.http import JsonResponse
import requests
import json
db = settings.firestore_db
FIREBASE_API_KEY = "AIzaSyCgf2cpIwqhkNh0k6OBhFGDLlPGQH2Qee0"

# === HÀM KIỂM TRA ADMIN (giữ nguyên) ===
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


def register(request):
    redirect_to = check_role_admin(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'dashboard':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')

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
        
        # === BẮT ĐẦU CHỈNH SỬA: DỊCH LỖI ĐĂNG KÝ (SỬA LẠI) ===
        except Exception as e: # Bắt tất cả lỗi từ Firebase
            error_message = str(e)
            print(f"Firebase Register Error: {error_message}") # Dùng để debug

            if "EMAIL_EXISTS" in error_message or "EmailAlreadyExistsError" in error_message:
                messages.error(request, 'Lỗi: Email này đã tồn tại trong hệ thống.')
            elif "WEAK_PASSWORD" in error_message or "Password must be at least 6 characters" in error_message:
                 messages.error(request, 'Lỗi: Mật khẩu quá yếu, cần ít nhất 6 ký tự.')
            elif "INVALID_EMAIL" in error_message:
                 messages.error(request, 'Lỗi: Định dạng email không hợp lệ.')
            else:
                 # Lỗi chung, không hiển thị tiếng Anh
                messages.error(request, f'Lỗi không xác định khi tạo tài khoản.')
        # === KẾT THÚC CHỈNH SỬA ===
            
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
                # === LOGIC DỊCH LỖI ĐĂNG NHẬP (giữ nguyên) ===
                error_message = data.get('error', {}).get('message', 'UNKNOWN_ERROR')
                print(f"Firebase Auth Error: {error_message}") # Dùng để debug

                if messages.get_messages(request):
                    list(messages.get_messages(request))

                if error_message == 'EMAIL_NOT_FOUND':
                    messages.error(request, 'Lỗi: Không tìm thấy tài khoản với email này.')
                elif error_message == 'INVALID_PASSWORD':
                    messages.error(request, 'Lỗi: Sai mật khẩu.')
                elif error_message == 'USER_DISABLED':
                    messages.error(request, 'Lỗi: Tài khoản này đã bị vô hiệu hóa.')
                else:
                    messages.error(request, 'Lỗi: Sai email hoặc mật khẩu.')

        except Exception as e:
            messages.error(request, f'Lỗi kết nối: {str(e)}')
    return render(request, 'accounts/login.html')

def logout_view(request):
    if 'firebase_user' in request.session:
        del request.session['firebase_user']
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('login')


def showall(request):
    redirect_to = check_role_admin(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'dashboard':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')

    # === LOGIC TÌM KIẾM THEO TÊN VÀ SĐT (giữ nguyên) ===
    keyword = request.GET.get('q', None)
    
    user_ref = db.collection('users').get()
    user_list = []

    for user in user_ref:
        item = user.to_dict()
        item['id'] = user.id

        if keyword:
            keyword_lower = keyword.lower()
            name_lower = item.get('name', '').lower()
            phone_lower = item.get('phone', '').lower() 

            if keyword_lower in name_lower or keyword_lower in phone_lower:
                user_list.append(item)
        
        else:
            user_list.append(item) 

    context = {
        'users': user_list
    }
    return render(request, 'accounts/showall.html', context)


def delete(request, user_id):
    redirect_to = check_role_admin(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'dashboard':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')

    if request.method == 'POST':
        db.collection('users').document(user_id).delete()
        return redirect(showall)
    
def update(request, user_id):
    redirect_to = check_role_admin(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'dashboard':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')

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