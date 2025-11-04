from django.shortcuts import render, redirect
from logistic_nhom03 import settings
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import ExportsForm
from datetime import datetime
# Create your views here.
db = settings.firestore_db

def showall(request):
    firebase_user = request.session['firebase_user']
    if not firebase_user:
        return redirect('login')
    try:
        exports_ref = db.collection('exports').get()
        exports = []
        for doc in exports_ref:
            item = doc.to_dict()
            item['deadline'] = 'Còn hạn giao'
            if timezone.now() > item.get('delivered_at'):
                item['deadline'] = 'Trễ hạn giao'
            item['id'] = doc.id
            exports.append(item)
        
        context = {
            'exports': exports
        }
        return render(request, 'exports/showall.html', context)
    except Exception as e:
        messages.error(request, f'Lỗi khi tải danh sách sản phẩm:{e}')
        return JsonResponse({'err': e})
    

def create(request):
    if request.method == 'POST':
        form = ExportsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['status'] = 'pending'
            data['created_at'] = timezone.now().isoformat() 
            data['delivered_at'] = data.get('delivered_at').isoformat()
            data['created_by'] = request.session['firebase_user'].get('displayName')
            print(data['delivered_at'])
            request.session['craft_export'] = data
            product_ref = db.collection('products').get()
            products = []
            for doc in product_ref:
                item = doc.to_dict()
                item['id'] = doc.id
                products.append(item)
            context = {
                'products': products
            }
            return render(request, 'exports/chooseproducts.html', context)
        print(form)
        return JsonResponse({'test': 'không tồn tại form ok'})

    else:
        return render(request, 'exports/create.html')
    
def chooseproduct(request):
    if request.method == 'POST':
        product_ref = db.collection('products').get()
        products_id = []

        for doc in product_ref:
            products_id.append(doc.id)
        
        quantity_list = {}
        id_list = []
        for id in products_id:
            if(request.POST.get("quantity_"+id) != ''):
                quantity_list[id] = request.POST.get("quantity_"+id)
                id_list.append(id)
        export = request.session['craft_export']
        export['products'] = quantity_list
        export['delivered_at'] = datetime.fromisoformat(export.get('delivered_at'))
        export['created_at'] = datetime.fromisoformat(export.get('created_at'))
        try:
            for id in id_list:
                print(id)
                product_ref = db.collection('products').document(id).get()
                product = product_ref.to_dict()
                quantity_before = int(product.get('quantity'))
                print(quantity_before)
                print(quantity_list.get(id))
                if(quantity_before >  int(quantity_list.get(id))):
                    quantity_after = quantity_before - int(quantity_list.get(id)) 
                    updated_by = request.session['firebase_user'].get('displayName')
                    print(updated_by)
                    try:
                        db.collection('products').document(id).update({'quantity': quantity_after, 'update_by': updated_by})
                        messages.success(request, "đã trừ số lượng")
                    except Exception as e:
                        print(e)
                        return JsonResponse({'err': "Cứu t với bây ơi lỗi cập nhật số lượng product"})
                else:
                    return JsonResponse({'err': "Số lượng xuất phai bé hơn nghe chưa"})
             
            db.collection('exports').add(export)
            del request.session['craft_export'] 
            messages.success(request, "Lụm gạo")
            return redirect('showallExports')
        except Exception as e:
            print(e)
            return JsonResponse({'Err': "Lỗi rồi người đẹp "})
    else:
        return redirect('showallExports')


def detail(request, export_id):
    doc_ref = db.collection('exports').document(export_id).get()
    export = doc_ref.to_dict()
    export['id'] = export_id
    product_list = {}
    for product in export.get('products'):
        product_name = db.collection('products').document(product).get().to_dict().get('name')
        print(export.get('products')[product])
        product_list[product_name] = export.get('products')[product]

    export['products'] = product_list
    context = {
        'export': export
    }
    return render(request, 'exports/detail.html', context)

def imports(request):
    product_ref = db.collection('products').get()
    product_list = []
    for product in product_ref:
        item = product.to_dict()
        item['id'] = product.id
        product_list.append(item)
    context = {
        'products': product_list
    }
    if request.method == 'POST':
        quantity_list = request.POST
        quantity_list_filter = {}
        
        for id in quantity_list:
            if request.POST.get(id) != '' and id != 'csrfmiddlewaretoken':
                quantity_list_filter[id] = request.POST.get(id)      
                product = db.collection('products').document(id).get().to_dict()
                quantity_before = int(product.get('quantity'))
                quantity_after = quantity_before + int(request.POST.get(id))
                print(quantity_after)
                db.collection('products').document(id).update({'quantity': quantity_after, 'update_by': request.session['firebase_user'].get('displayName')})

        return redirect('showallProduct')

    else:
        return render(request, 'exports/import.html', context)