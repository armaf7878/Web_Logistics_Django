from django.shortcuts import render, redirect
from django.contrib import messages
from logistic_nhom03 import settings
from django.http import JsonResponse
from django.utils import timezone
from firebase_admin import firestore
from django.views.decorators.csrf import csrf_exempt
import json
import requests

db = settings.firestore_db
def showall(request):
    deliver_id = request.session['firebase_user'].get('localId')
    docs_ref = db.collection('exports').order_by('pickup_time').get()
    exports = []
    product_list = {}
    for doc in docs_ref:
        item = doc.to_dict()
        if item.get('assigned_to') == deliver_id and item.get('status') == 'pending':
            item['id'] = doc.id
            for product_id in item['products']:
                product_name = db.collection('products').document(product_id).get().to_dict().get('name')           
                product_list[product_name] = item['products'].get(product_id)
                item['products'] = product_list
            exports.append(item)
            product_list = {}
    print(exports)
    
    
    if not exports:
        valid = 'Không có đơn nào hết'
        context = {
             'valid': valid,
             'name': request.session['firebase_user'].get('displayName')
         }
        return render(request, 'deliver/showall.html', context)
    context = {
         'exports': exports,
        'name': request.session['firebase_user'].get('displayName')
    }
    return render(request, 'deliver/showall.html', context)

def processing(request, export_id):
    deliver_id = request.session['firebase_user'].get('localId')
    export_ref = db.collection('exports').get()
    for doc in export_ref:
        export = doc.to_dict()
        if(export.get('assigned_to') == deliver_id and export.get('status') == 'delivering'):
            messages.error(request, 'Bạn đang giao đơn khác rồi, không thể nhận thêm vào lúc này')
            return redirect('deliver')
    
    export = db.collection('exports').document(export_id).get().to_dict()
    db.collection('exports').document(export_id).update({'status': 'delivering'})
    db.collection('delivery-tracking').document(deliver_id).set({
        'ware_house': firestore.GeoPoint(10.7843925, 106.6938095),
        'destination': export.get('address'), 
        'last_update': timezone.now(),
        'current_location': firestore.GeoPoint(10.796937403442016, 106.67368546418707),
        'export_id': export_id,
    })
    messages.success(request, 'Bạn đã xác nhận lấy hàng thành công, hãy chuyển qua đơn đang tiếp nhận')
    context = {
        'name': request.session['firebase_user'].get('displayName')
    }   
    return redirect('deliver')

def getcordinates(address, latitude=None, longitude=None):
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
    if latitude and longitude:
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

def delivering(request):
    deliver_id = request.session['firebase_user'].get('localId')
    print(deliver_id)
    tracking = db.collection('delivery-tracking').document(deliver_id).get()
    print(tracking)
    if(not tracking.exists):
        return redirect('deliver')
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
        'deliver_id': deliver_id,
        'export_id': export_id
    }
    return render(request, 'deliver/delivering.html', context)


@csrf_exempt
def update_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        deliver_id = data.get("deliver_id")
        lat = data.get("latitude")
        lon = data.get("longitude")
        db.collection("delivery-tracking").document(deliver_id).update({
            "current_location": firestore.GeoPoint(lat, lon),
            "last_update": timezone.now(),
        })
        return JsonResponse({"message": "Cập nhật vị trí thành công"})
    
def complete(request):
    if request.method == 'POST':
        export_id = request.POST.get('export_id')
        deliver_id = request.POST.get('deliver_id')
        print(export_id)
        db.collection('exports').document(export_id).update({"status":"delivered"})

        data = db.collection('delivery-tracking').document(deliver_id).get().to_dict()
        data['deliver_id'] = deliver_id
        db.collection('inventory_logs').add(data)
        db.collection('delivery-tracking').document(deliver_id).delete()
        return redirect('deliver')
        