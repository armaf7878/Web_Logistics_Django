from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import firestore
from django.http import JsonResponse
from logistic_nhom03 import settings
import requests 
import json 
db = settings.firestore_db
def dashboard(request):
    try: 
        firebase_user = request.session.get('firebase_user')
        if not firebase_user:
            messages.error(request, 'Bạn phải đăng nhập để xem trang này.')
            return redirect('login')
            
        user_id = request.session['firebase_user'].get('localId')
        
        # === BẮT ĐẦU THÊM MỚI: KIỂM TRA VAI TRÒ TÀI XẾ ===
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            messages.error(request, 'Không tìm thấy thông tin người dùng.')
            return redirect('login')
        
        role = user_doc.to_dict().get('role')
        if role == 'deliver':
            messages.error(request, 'Tài khoản tài xế không có quyền truy cập trang này.')
            return redirect('deliver') # Chuyển hướng tài xế về trang của họ
        # === KẾT THÚC THÊM MỚI ===

    except Exception as e:
        # Sửa lỗi logic: nếu session không có 'firebase_user' thì sẽ báo lỗi
        # Gộp chung vào đây
        messages.error(request, 'Bạn phải đăng nhập để xem trang này.')
        return redirect('login')

    name = firebase_user.get('displayName')  
    # role đã được lấy ở trên
    context= {
        'name': name,
        'role': role
    } 
    return render(request ,'dashboard/dashboard.html', context)