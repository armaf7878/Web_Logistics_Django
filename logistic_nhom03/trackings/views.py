from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from logistic_nhom03 import settings
import requests

db = settings.firestore_db

# === BẮT ĐẦU THÊM MỚI: HÀM KIỂM TRA VAI TRÒ ===
def check_role_deliver(request):
    try:
        if 'firebase_user' not in request.session:
            return 'login' # Yêu cầu đăng nhập
        
        user_id = request.session['firebase_user'].get('localId')
        user_doc = db.collection('users').document(user_id).get()

        if not user_doc.exists:
            return 'login' # Không tìm thấy user
        
        role = user_doc.to_dict().get('role')

        if role == 'deliver':
            return 'deliver' # Là tài xế, chuyển hướng về trang deliver
            
    except Exception as e:
        return 'login' # Lỗi khác thì cứ redirect về login
    
    return None # Không phải tài xế, cho phép truy cập
# === KẾT THÚC THÊM MỚI ===

def getcordinates(address, latitude = None, longitude = None):
    url = 'https://nominatim.openstreetmap.org/search'
    if address:
        params = {
            'q': address,
            'format': 'jsonv2',
            'limit': 1
        }
        headers = {'User-Agent': 'logistic_nhom03/1.0 (contact: danh@example.com)'}
        res = requests.get(url, params=params, headers=headers, timeout=10)
        print(res)
        if res.status_code == 200 and res.json():
            data = res.json()[0]
            print(res.json)
            lat, lon = data['lat'], data['lon']
            return lat, lon
        else:
            return JsonResponse({'error': 'Không tìm thấy vị trí'}, status=404)
    if latitude:
        geo = f"{latitude},{longitude}"
        params = {
            'q' : geo,
            'format' : 'jsonv2',
            'limit': 1
        } 
        headers = {'User-Agent': 'logistic_nhom03/1.0 (contact: danh@example.com)'}

        res = requests.get(url, params=params, headers=headers, timeout=10)
        print(res.url)
        print(res)
        if res.status_code == 200 and res.json():
            data = res.json()[0]
            print(data['display_name'])
            return data['display_name']
        else:
            return JsonResponse({'error': 'Không tìm thấy vị trí'}, status=404)


    
def showall(request):
    # === BẮT ĐẦU THÊM MỚI: GỌI HÀM KIỂM TRA ===
    redirect_to = check_role_deliver(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để xem trang này.')
        return redirect('login')
    if redirect_to == 'deliver':
        messages.error(request, 'Tài khoản tài xế không có quyền truy cập trang này.')
        return redirect('deliver')
    # === KẾT THÚC THÊM MỚI ===

    if request.session.get('firebase_user'):
        tracking_ref = db.collection('delivery-tracking').get()
        tracking = []
        for doc in tracking_ref:
            item = doc.to_dict()
            item['id'] = doc.id
            item['longitude'] = item['current_location'].longitude
            item['latitude'] = item['current_location'].latitude
            item['displayName'] = getcordinates('', item.get('latitude') , item.get('longitude'))
            tracking.append(item)
        context = {
            'tracking': tracking
        }
        return render(request,'trackings/showall.html', context)
    else:
        return redirect('login')

def detail(request, tracking_id):
    # === BẮT ĐẦU THÊM MỚI: GỌI HÀM KIỂM TRA ===
    redirect_to = check_role_deliver(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để xem trang này.')
        return redirect('login')
    if redirect_to == 'deliver':
        messages.error(request, 'Tài khoản tài xế không có quyền truy cập trang này.')
        return redirect('deliver')
    # === KẾT THÚC THÊM MỚI ===

    tracking = db.collection('delivery-tracking').document(tracking_id).get()
    print(tracking)
    if(not tracking.exists):
        return redirect('showall')
    tracking = tracking.to_dict()
    print(tracking.get('destination'))
    destination_lat, destination_lon = getcordinates(tracking.get('destination'))
    ware_house_lat = tracking['ware_house'].latitude
    ware_house_lon = tracking['ware_house'].longitude
    current_deliver_lat = tracking['current_location'].latitude
    current_deliver_lon = tracking['current_location'].longitude
    export_id = tracking.get('export_id')
    context = {
        'destination_lat': destination_lat,
        'destination_lon': destination_lon,
        'ware_house_lat': ware_house_lat,
        'ware_house_lon': ware_house_lon,
        'current_deliver_lat': current_deliver_lat,
        'current_deliver_lon': current_deliver_lon,
        'export_id': export_id
    }
    return render(request, 'trackings/detail.html', context)