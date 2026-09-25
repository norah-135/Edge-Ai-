import os
import numpy as np
from sklearn.svm import OneClassSVM
from micromlgen import port

# تحديد مسار المجلد الحالي للمشروع بدقة
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "my_keystrokes.csv")
OUTPUT_HEADER_PATH = os.path.join(BASE_DIR, "model.h")

# 1. التحقق من وجود ملف البيانات
if not os.path.exists(CSV_PATH):
    # في حال تم حفظه بالخطأ في مسار التيرمنال، نبحث عنه هناك
    if os.path.exists("my_keystrokes.csv"):
        CSV_PATH = "my_keystrokes.csv"
    else:
        raise FileNotFoundError(f"Could not find 'my_keystrokes.csv'. Please make sure it exists in: {BASE_DIR}")

print(f"Loading data from: {CSV_PATH}")
X = np.genfromtxt(CSV_PATH, delimiter=',')

# 2. تدريب النموذج مع تحديد gamma كرقم عشري صريح
# micromlgen يتطلب قيمة float صريحة لـ gamma
clf = OneClassSVM(kernel='rbf', gamma=0.01, nu=0.1)
clf.fit(X)

# 3. تصدير النموذج إلى C++
c_code = port(clf, class_name="KeystrokeClassifier")

with open(OUTPUT_HEADER_PATH, 'w') as f:
    f.write(c_code)

print("=" * 60)
print(f"[SUCCESS] 'model.h' has been created successfully!")
print(f"File location: {OUTPUT_HEADER_PATH}")
print("=" * 60)