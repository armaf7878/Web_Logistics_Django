from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from logistic_nhom03 import settings
import requests

db = settings.firestore_db

def getcordinates(address, latitude, longitude):
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
            return JsonResponse({'address': address, 'lat': lat, 'lon': lon})
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
    doc_ref = db.collection('delivery-tracking').document(tracking_id).get()
    if not doc_ref.exists:
        respone = HttpResponse("<h1>Shipper chưa chấp nhận đơn hàng, đợi chuyển hướng....</h1>")
        respone['Refresh'] = '3; url=/trackings/'

        return respone
    tracking = doc_ref.to_dict()
    tracking['current_longitude'] = tracking['current_location'].longitude
    tracking['current_latitude'] = tracking['current_location'].latitude
    tracking.pop('current_location')
    context = {
        'tracking' : tracking
    }
    return render(request, 'trackings/detail.html', context)