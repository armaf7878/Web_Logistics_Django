from django.shortcuts import render, redirect
from logistic_nhom03 import settings
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import ExportsForm
from datetime import datetime
from datetime import timedelta
# Create your views here.
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

    firebase_user = request.session['firebase_user']
    if not firebase_user:
        return redirect('login')
    try:
        exports_ref = db.collection('exports').get()
        exports = []
        for doc in exports_ref:
            item = doc.to_dict()
            item['deadline'] = 'Còn hạn lấy'
            if timezone.now() > item.get('pickup_time'):
                item['deadline'] = 'Trễ hạn lấy'
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
    # === BẮT ĐẦU THÊM MỚI: GỌI HÀM KIỂM TRA ===
    redirect_to = check_role_deliver(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'deliver':
        messages.error(request, 'Tài khoản tài xế không có quyền truy cập trang này.')
        return redirect('deliver')
    # === KẾT THÚC THÊM MỚI ===

    if request.method == 'POST':
        form = ExportsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['status'] = 'pending'
            data['created_at'] = timezone.now().isoformat() 
            data['created_by'] = request.session['firebase_user'].get('displayName')
            data['pickup_time'] = data.get('pickup_time').isoformat()
            print(type(data.get('pickup_time')))
            print(data['pickup_time'])
            request.session['craft_export'] = data
            deliver_ref = db.collection('users').get()
            deliver_list = []
            for doc in deliver_ref:
                user = doc.to_dict()
                if user.get('role') == 'deliver':
                    deliver_list.append(doc.id)
                print("danh sách ban đầu" + str(deliver_list))
            if len(deliver_list) > 0:
                exports_ref = db.collection('exports').get()
                for export in exports_ref:
                    item = export.to_dict()
                    
                    for deliverID in deliver_list:
                        if item.get('assigned_to') == deliverID:
                            deliver_list.remove(deliverID)
                    print("============================") 
                    print("danh sách lọc" + str(deliver_list)) 
                    diff =(item.get('pickup_time') - datetime.fromisoformat(data.get('pickup_time')))
                    print(str(diff))
                    if abs(diff) > timedelta(days=7) :
                        deliver_list.append(item.get('assigned_to'))
                    print("============================") 
                    print("danh sách thêm" + str(deliver_list))
            deliver_list_name = []
            for deliver in deliver_list:
                print(str(deliver))
                doc_ref = db.collection('users').document(deliver).get()
                item = doc_ref.to_dict()
                item['id'] = doc_ref.id
                deliver_list_name.append(item)
            product_ref = db.collection('products').get()
            products = []
            for doc in product_ref:
                item = doc.to_dict()
                item['id'] = doc.id
                products.append(item)
            context = {
                'products': products,
                'deliver': deliver_list_name
            }
            return render(request, 'exports/chooseproducts.html', context)

        return JsonResponse({'test': 'không tồn tại form ok'})

    else:
        return render(request, 'exports/create.html')
    
def chooseproduct(request):
    # === BẮT ĐẦU THÊM MỚI: GỌI HÀM KIỂM TRA ===
    redirect_to = check_role_deliver(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'deliver':
        messages.error(request, 'Tài khoản tài xế không có quyền truy cập trang này.')
        return redirect('deliver')
    # === KẾT THÚC THÊM MỚI ===

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
        export['created_at'] = datetime.fromisoformat(export.get('created_at'))
        export['pickup_time'] = datetime.fromisoformat(export.get('pickup_time'))
        export['assigned_to'] = request.POST.get('assigned_to')
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
    # === BẮT ĐẦU THÊM MỚI: GỌI HÀM KIỂM TRA ===
    redirect_to = check_role_deliver(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để xem trang này.')
        return redirect('login')
    if redirect_to == 'deliver':
        messages.error(request, 'Tài khoản tài xế không có quyền truy cập trang này.')
        return redirect('deliver')
    # === KẾT THÚC THÊM MỚI ===

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
    # === BẮT ĐẦU THÊM MỚI: GỌI HÀM KIỂM TRA ===
    redirect_to = check_role_deliver(request)
    if redirect_to == 'login':
        messages.error(request, 'Bạn phải đăng nhập để thực hiện việc này.')
        return redirect('login')
    if redirect_to == 'deliver':
        messages.error(request, 'Tài khoản tài xế không có quyền truy cập trang này.')
        return redirect('deliver')
    # === KẾT THÚC THÊM MỚI ===

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