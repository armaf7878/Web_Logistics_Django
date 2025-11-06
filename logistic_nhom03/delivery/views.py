from django.shortcuts import render, redirect
from django.contrib import messages
from logistic_nhom03 import settings
from django.http import JsonResponse
from django.utils import timezone
from firebase_admin import firestore

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
        'ware_house': firestore.GeoPoint(10.800137016114975, 106.65438400856388),
        'destination': export.get('address'), 
        'last_update': timezone.now(),
        'current_location': firestore.GeoPoint(10.2, 30.2),
    })
    messages.success(request, 'Bạn đã xác nhận lấy hàng thành công, hãy chuyển qua đơn đang tiếp nhận')
    context = {
        'name': request.session['firebase_user'].get('displayName')
    }   
    return redirect('deliver')
