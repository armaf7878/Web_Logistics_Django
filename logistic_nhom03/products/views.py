from django.shortcuts import render, redirect
from logistic_nhom03 import settings
from django.contrib import messages
from django.http import JsonResponse
from .models import ProductForm
from django.utils import timezone
db = settings.firestore_db
# Create your views here.

def showall(request):
    firebase_user = request.session.get('firebase_user')
    if not firebase_user:
        return redirect('login')    
    if request.method == 'POST':
        keyword =  request.POST.get('sort_name').lower()
        print(keyword)
        docs = db.collection('products').get()
        products = []
        for doc in docs:
            p = doc.to_dict()
            p['id'] = doc.id
            print(p.get('name').lower())
            if keyword in p.get('name').lower():
                products.append(p)
        
        context = {
            'products': products,
           
        }

        return render(request, 'products/showall.html', context)
    else:
        try:
            production_ref = db.collection('products').get()
            products = []
            for doc in production_ref:
                item = doc.to_dict()
                item['id'] = doc.id  
                products.append(item)

            name = firebase_user.get('displayName')
            context = {
            'name': name,
            'products': products
            }
            return render(request, 'products/showall.html', context)
        except Exception as e :
            messages.error(request, f'Lỗi khi tải danh sách sản phẩm:{e}')
            return render(request, 'products/showall.html', {'name': name})
    
def delete(request, product_id):
    try:
        doc_ref = db.collection('products').document(product_id)
        doc =doc_ref.get()
        
        if not doc.exists:
            messages.error(request, f"Sản phẩm không tồn tại'{product_id}'")
        else:
            doc_ref.delete()
            print("HERE")
            messages.success(request, f"Đã xóa sản phẩm:{product_id}")
    except Exception as e:
        messages.error(request, f"Lỗi khi xóa {e}")
    return redirect('showallProduct')


def create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['update_by'] = request.session['firebase_user'].get('displayName')
            data['import_date'] = timezone.now()
            try:
                db.collection('products').add(data)
                messages.success(request, f'Đã thêm sản phẩm{data['name']}')
                return redirect('showallProduct')
            except Exception as e:
                    messages.error(request, f"Lỗi khi thêm sản phẩm: {e}")
        else:
            messages.error(request, "Dữ liệu nhập chưa hợp lệ!")
    else:
        return render(request, 'products/create.html')

def update(request, product_id):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['update_by'] = request.session['firebase_user'].get('displayName')
            db.collection('products').document(product_id).update(data)
            messages.success(request, "Cập nhật thành công!")
            return redirect('showallProduct')
        else:
            return JsonResponse({'err':"Lỗi khi cập nhật sản phẩm"})
    else:
        try:
            doc_ref = db.collection('products').document(product_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                messages.error(request, f"Sản phẩm không tồn tại")
            else:
                product = doc.to_dict()
                print(product)
                context = {
                    'product': product,
                    'productID': doc_ref.id
                }
                return render(request, 'products/update.html', context)
        except Exception as e:
            messages.error(request, f"Lỗi khi cập nhật {e}")
            return redirect('showallProduct')