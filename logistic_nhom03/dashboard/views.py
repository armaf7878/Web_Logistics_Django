from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import firestore
from django.http import JsonResponse
from logistic_nhom03 import settings
import requests 
import json 
db = settings.firestore_db
def dashboard(request):
    firebase_user = request.session.get('firebase_user')
    user_id = request.session['firebase_user'].get('localId')
    print(user_id)
    if not firebase_user:
        return redirect('login')
    name = firebase_user.get('displayName')  
    role = db.collection('users').document(user_id).get().to_dict().get('role')
    context= {
        'name': name,
        'role': role
    } 
    return render(request ,'dashboard/dashboard.html', context)
  
    