# Database Quick Start Guide

## 📍 Database Lưu Ở Đâu?

### SQLite (Mặc định - Không cần cài thêm gì)

**Vị trí:** `backend/combo_optimizer.db`

Đây là **file database** (giống như file Excel), không cần server:
- ✅ File nằm ngay trong thư mục `backend/`
- ✅ Không cần cài PostgreSQL hay MySQL
- ✅ Không cần chạy server
- ✅ Chỉ cần Python và SQLAlchemy

**Ví dụ đường dẫn:**
```
D:\Trade\Demo1\v1.4\backend\combo_optimizer.db
```

---

## 🔧 Cần Cài Gì?

### Đã có trong requirements.txt:
- ✅ `sqlalchemy==2.0.23` - ORM để làm việc với database
- ✅ `alembic==1.12.1` - Tool để quản lý migrations

### Không cần cài thêm:
- ❌ PostgreSQL (nếu dùng SQLite)
- ❌ MySQL
- ❌ Database server nào cả
- ❌ Phần mềm bên ngoài

**SQLite là built-in** trong Python, chỉ cần SQLAlchemy để làm việc với nó.

---

## 🚀 Cách Chạy Database

### Bước 1: Cài Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Lệnh này sẽ cài:
- sqlalchemy
- alembic

### Bước 2: Khởi Tạo Database

```bash
python database/init_database.py
```

**Kết quả:**
- Tạo file `combo_optimizer.db` trong thư mục `backend/`
- Tạo tất cả tables cần thiết

### Bước 3: Migrate Data Từ JSON

```bash
python database/migrate_json.py
```

**Kết quả:**
- Copy tất cả strategies từ JSON files sang database
- Verify migration thành công

### Bước 4: Test Database

```bash
python -c "from database.connection import get_db_session; from database.models import Strategy; db = get_db_session(); print('Strategies:', db.query(Strategy).count()); db.close()"
```

---

## 📂 Cấu Trúc File

Sau khi chạy, bạn sẽ có:

```
backend/
├── combo_optimizer.db          ← Database file (SQLite)
├── saved_strategies/           ← JSON files (backup)
│   ├── RSI_Strategy.json
│   └── ...
└── database/
    ├── models.py              ← Database models
    ├── connection.py          ← Kết nối database
    ├── repositories.py         ← CRUD operations
    ├── init_database.py       ← Script khởi tạo
    └── migrate_json.py        ← Script migrate
```

---

## ✅ Kiểm Tra Database Đã Chạy Chưa

### Cách 1: Kiểm tra file

```bash
cd backend
dir combo_optimizer.db
```

Nếu có file → Database đã được tạo

### Cách 2: Test Python

```python
from database.connection import get_db_session
from database.models import Strategy

db = get_db_session()
try:
    count = db.query(Strategy).count()
    print(f"✅ Database OK! Có {count} strategies")
finally:
    db.close()
```

### Cách 3: Kiểm tra bằng SQLite Browser (Optional)

Có thể dùng tool như **DB Browser for SQLite** để xem database:
- Download: https://sqlitebrowser.org/
- Mở file `combo_optimizer.db`
- Xem tables và data

---

## 🔄 Chuyển Từ JSON Sang Database

### Hiện tại (JSON):
```python
from strategy_storage import strategy_storage  # Dùng JSON files
```

### Sau khi migrate (Database):
```python
from strategy_storage_db import strategy_storage  # Dùng database
```

**Chỉ cần đổi import**, code còn lại giữ nguyên!

---

## 🎯 Khi Nào Cần PostgreSQL?

**Chỉ cần PostgreSQL khi:**
- ✅ Production environment
- ✅ Nhiều người dùng cùng lúc
- ✅ Cần network access
- ✅ High traffic

**Với development/personal use:**
- ✅ SQLite là đủ
- ✅ Không cần cài thêm gì
- ✅ File-based, dễ backup

---

## 📝 Tóm Tắt

| Câu hỏi | Trả lời |
|---------|---------|
| **Database lưu ở đâu?** | `backend/combo_optimizer.db` (file SQLite) |
| **Cần cài phần mềm gì?** | Chỉ cần `pip install -r requirements.txt` |
| **Cần PostgreSQL không?** | Không, SQLite đủ cho development |
| **Cần chạy server không?** | Không, SQLite là file-based |
| **Làm sao biết đã chạy?** | Kiểm tra file `combo_optimizer.db` |

---

## 🚨 Troubleshooting

### Lỗi: "No module named 'sqlalchemy'"
**Giải pháp:**
```bash
pip install sqlalchemy alembic
```

### Lỗi: "Database file not found"
**Giải pháp:**
```bash
python database/init_database.py
```

### Lỗi: "Table already exists"
**Giải pháp:**
Database đã được tạo rồi, không cần chạy lại init.

---

**Status:** ✅ Sẵn sàng sử dụng  
**Next:** Chạy `python database/init_database.py` để tạo database

