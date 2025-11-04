from settings import firestore_db

doc = firestore_db.collection('test').document('demo')
doc.set({'msg': 'Hello'})
print("✅ Ghi dữ liệu thành công")