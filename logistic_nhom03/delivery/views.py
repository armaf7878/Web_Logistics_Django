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
    docs_ref = db.collection('exports').get()
    export = {}
    product_list = {}
    for doc in docs_ref:
        item = doc.to_dict()
        if item.get('assigned_to') == deliver_id and item.get('status') == 'status':
            export = item
            export['id'] = doc.id
            for product_id in export['products']:
                product_name = db.collection('products').document(product_id).get().to_dict().get('name')
                product_list[product_name] = export['products'].get(product_id)

    
    if not export:

        export['valid'] = 'Không có đơn nào hết'
        context = {
            'export': export,
            'name': request.session['firebase_user'].get('displayName')
        }
        return render(request, 'deliver/showall.html', context)
    export['products'] = product_list
    context = {
        'export': export,
        'name': request.session['firebase_user'].get('displayName')
    }
    return render(request, 'deliver/showall.html', context)

def processing(request, export_id):
    deliver_id = request.session['firebase_user'].get('localId')
    export = db.collection('exports').document(export_id).get().to_dict()
    db.collection('exports').document(export_id).update({'status': 'delivering'})
    db.collection('delivery-tracking').document(deliver_id).set({
        'ware_house': firestore.GeoPoint(10.800137016114975, 106.65438400856388),
        'destination': export.get('address'), 
        'last_update': timezone.now(),
        'current_location': firestore.GeoPoint(10.2, 30.2),
    })
    context = {
        'name': request.session['firebase_user'].get('displayName')
    }   
    return redirect(request, 'deliver/processing.html', context)
