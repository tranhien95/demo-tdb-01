# Hướng Dẫn Setup Database

## 📍 Database Lưu Ở Đâu?

**Vị trí:** `backend/combo_optimizer.db`

Đây là **file SQLite** (giống file Excel), không phải server:
- ✅ File nằm trong thư mục `backend/`
- ✅ Không cần cài PostgreSQL/MySQL
- ✅ Không cần chạy server
- ✅ Chỉ cần Python + SQLAlchemy

**Ví dụ đường dẫn đầy đủ:**
```
D:\Trade\Demo1\v1.4\backend\combo_optimizer.db
```

---

## 🔧 Cần Cài Gì?

### ✅ Đã có trong requirements.txt:
- `sqlalchemy==2.0.23` - Thư viện làm việc với database
- `alembic==1.12.1` - Tool quản lý migrations

### ❌ KHÔNG cần cài:
- PostgreSQL
- MySQL  
- Database server nào cả
- Phần mềm bên ngoài

**SQLite là built-in trong Python**, chỉ cần SQLAlchemy để làm việc với nó.

---

## 🚀 Các Bước Setup

### Bước 1: Cài Dependencies

Mở terminal/PowerShell trong thư mục `backend`:

```bash
cd D:\Trade\Demo1\v1.4\backend
pip install sqlalchemy alembic
```

Hoặc cài tất cả:
```bash
pip install -r requirements.txt
```

### Bước 2: Khởi Tạo Database

```bash
python database/init_database.py
```

**Kết quả:**
- ✅ Tạo file `combo_optimizer.db` 
- ✅ Tạo tất cả tables

### Bước 3: Migrate Data Từ JSON

```bash
python database/migrate_json.py
```

**Kết quả:**
- ✅ Copy strategies từ JSON → Database
- ✅ Verify migration

---

## ✅ Kiểm Tra Database

### Cách 1: Kiểm tra file

```bash
cd backend
dir combo_optimizer.db
```

Nếu thấy file → ✅ Database đã được tạo

### Cách 2: Test bằng Python

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

### Cách 3: Dùng SQLite Browser (Optional)

Tool để xem database trực quan:
- Download: https://sqlitebrowser.org/
- Mở file `combo_optimizer.db`
- Xem tables và data

---

## 📂 Cấu Trúc Sau Khi Setup

```
backend/
├── combo_optimizer.db          ← Database file (SQLite)
├── saved_strategies/           ← JSON files (backup)
│   ├── RSI_Strategy.json
│   └── ...
└── database/
    ├── models.py
    ├── connection.py
    └── ...
```

---

## 🔄 Chuyển Sang Dùng Database

### Hiện tại (JSON):
```python
from strategy_storage import strategy_storage
```

### Sau khi migrate (Database):
```python
from strategy_storage_db import strategy_storage
```

**Chỉ cần đổi import**, code còn lại giữ nguyên!

---

## ❓ FAQ

### Q: Database đã chạy chưa?
**A:** Chạy `python database/init_database.py` để tạo database.

### Q: Cần cài PostgreSQL không?
**A:** Không! SQLite đủ cho development. Chỉ cần PostgreSQL khi production.

### Q: Database file ở đâu?
**A:** `backend/combo_optimizer.db`

### Q: Làm sao backup database?
**A:** Chỉ cần copy file `combo_optimizer.db` là xong!

### Q: Có cần chạy server không?
**A:** Không! SQLite là file-based, không cần server.

---

## 🚨 Troubleshooting

### Lỗi: "No module named 'sqlalchemy'"
```bash
pip install sqlalchemy alembic
```

### Lỗi: "Database file not found"
```bash
python database/init_database.py
```

### Lỗi: "Table already exists"
→ Database đã được tạo rồi, không cần chạy lại.

---

## 📝 Tóm Tắt

| Câu hỏi | Trả lời |
|---------|---------|
| **Database lưu ở đâu?** | `backend/combo_optimizer.db` |
| **Cần cài gì?** | `pip install sqlalchemy alembic` |
| **Cần PostgreSQL?** | Không, SQLite đủ |
| **Cần server?** | Không, file-based |
| **Làm sao biết đã OK?** | Kiểm tra file `combo_optimizer.db` |

---

**Next Step:** Chạy `pip install sqlalchemy alembic` rồi `python database/init_database.py`

