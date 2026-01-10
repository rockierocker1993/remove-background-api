# Background Removal Service

Service API untuk menghilangkan background dari gambar menggunakan FastAPI dan rembg. Service ini mendukung deteksi otomatis jenis gambar (anime/foto) dan menghasilkan output dengan edge yang optimal untuk icon.

## Fitur

- ✨ Background removal otomatis menggunakan AI
- 🎨 Deteksi jenis gambar (anime/foto)
- 🖼️ Hard edge processing untuk icon
- ✂️ Auto crop hasil
- 🚀 REST API dengan FastAPI
- 🐳 Docker support

## Teknologi

- **FastAPI** - Web framework
- **rembg** - AI background removal
- **Pillow** - Image processing
- **OpenCV** - Image analysis
- **onnxruntime** - Model inference

## Quick Start

### Menggunakan Docker (Recommended)

1. Build dan jalankan dengan docker-compose:
```bash
docker-compose up -d
```

Service akan berjalan di `http://localhost:8000`

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Jalankan server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST `/remove-bg-icon`

Menghilangkan background dari gambar dan mengoptimalkan untuk icon.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File gambar (PNG, JPG, dll)

**Response:**
- Content-Type: `image/png`
- Body: Gambar PNG dengan background transparan

**Contoh menggunakan cURL:**
```bash
curl -X POST "http://localhost:8000/remove-bg-icon" \
  -F "file=@input.jpg" \
  --output result.png
```

**Contoh menggunakan Python:**
```python
import requests

url = "http://localhost:8000/remove-bg-icon"
files = {"file": open("input.jpg", "rb")}
response = requests.post(url, files=files)

with open("result.png", "wb") as f:
    f.write(response.content)
```

**Contoh menggunakan JavaScript:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/remove-bg-icon', {
  method: 'POST',
  body: formData
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'result.png';
  a.click();
});
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Cara Kerja

1. **Upload Gambar** - Client mengirim gambar melalui API
2. **Deteksi Jenis** - System mendeteksi apakah gambar adalah anime atau foto berdasarkan:
   - Saturasi warna (mean & std)
   - Edge density menggunakan Canny edge detection
3. **Remove Background** - Menggunakan model AI (isnet-general-use atau isnet-anime)
4. **Hard Edge Processing** - Alpha channel diproses dengan threshold untuk menghasilkan edge yang tajam (ideal untuk icon)
5. **Auto Crop** - Gambar di-crop otomatis sesuai bounding box
6. **Optimasi** - PNG dioptimasi untuk ukuran file lebih kecil

## Model AI

Service ini menggunakan dua model dari rembg:
- `isnet-general-use` - Untuk gambar foto/realistic
- `isnet-anime` - Untuk gambar anime/cartoon (saat ini default menggunakan general)

## Development

### Struktur Proyek
```
rembg-service/
├── app/
│   └── main.py          # FastAPI application
├── docker-compose.yml   # Docker compose config
├── Dockerfile          # Docker image config
├── requirements.txt    # Python dependencies
└── # Background Removal API

API service untuk menghapus background dari gambar dengan dukungan untuk pembuatan icon dan penggunaan umum.

## 📁 Struktur Project

```
remove-background-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point aplikasi
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Konfigurasi aplikasi
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── background_controller.py  # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── background_removal_service.py  # Business logic
│   │   └── image_service.py    # Image processing utilities
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   └── core/
│       ├── __init__.py
│       ├── exceptions.py       # Custom exceptions
│       └── middleware.py       # Custom middleware
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Fitur

- **Remove Background for Icons**: Menghapus background dengan hard edge, optimal untuk pembuatan icon
- **Remove Background Standard**: Menghapus background dengan soft edge untuk penggunaan umum
- **Auto Image Type Detection**: Deteksi otomatis apakah gambar anime atau foto
- **Auto Crop**: Crop otomatis untuk menghilangkan border transparan
- **Health Check**: Endpoint untuk monitoring status service

## 🛠️ Teknologi

- **FastAPI**: Modern web framework
- **Rembg**: Library untuk background removal
- **PIL/Pillow**: Image processing
- **OpenCV**: Computer vision operations
- **Pydantic**: Data validation

## 📦 Instalasi

### Menggunakan Docker (Recommended)

```bash
# Build dan jalankan
docker-compose up --build

# Atau jalankan di background
docker-compose up -d
```

### Manual Installation

```bash
# Clone repository
git clone <repository-url>
cd remove-background-api

# Buat virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Jalankan aplikasi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Konfigurasi

Edit file `.env` untuk mengatur konfigurasi:

```env
APP_NAME="Background Removal Service"
API_PREFIX="/api/v1"
MAX_FILE_SIZE=10485760  # 10MB
ICON_ALPHA_THRESHOLD=200
```

## 📖 API Endpoints

### 1. Remove Background for Icons
```http
POST /api/v1/remove-bg-icon
Content-Type: multipart/form-data

file: <image-file>
```

**Response**: PNG image dengan background transparan dan hard edge

### 2. Remove Background (Standard)
```http
POST /api/v1/remove-bg
Content-Type: multipart/form-data

file: <image-file>
```

**Response**: PNG image dengan background transparan dan soft edge

### 3. Health Check
```http
GET /api/v1/health
```

**Response**:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### 4. Root
```http
GET /
```

**Response**: Informasi API

## 📚 Dokumentasi API

Setelah aplikasi berjalan, akses:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Menggunakan curl
curl -X POST "http://localhost:8000/api/v1/remove-bg-icon" \
  -H "accept: image/png" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-image.jpg" \
  --output result.png

# Menggunakan Python
import requests

url = "http://localhost:8000/api/v1/remove-bg-icon"
files = {"file": open("your-image.jpg", "rb")}
response = requests.post(url, files=files)

with open("result.png", "wb") as f:
    f.write(response.content)
```

## 🏗️ Arsitektur

### Layer Pattern

1. **Controller Layer** (`controllers/`): 
   - Handle HTTP requests/responses
   - Validasi input
   - Route definitions

2. **Service Layer** (`services/`):
   - Business logic
   - Background removal processing
   - Image manipulation

3. **Model Layer** (`models/`):
   - Data schemas
   - Request/response models

4. **Core Layer** (`core/`):
   - Middleware
   - Exception handlers
   - Utilities

5. **Config Layer** (`config/`):
   - Application settings
   - Environment variables

## 🔍 Logging

Aplikasi mencatat setiap request dengan informasi:
- HTTP method dan path
- Status code
- Processing time
- Errors (jika ada)

## 🐳 Docker

```bash
# Build image
docker build -t remove-bg-api .

# Run container
docker run -p 8000:8000 remove-bg-api

# Dengan docker-compose
docker-compose up
```

## 📝 License

MIT License

## 👥 Contributing

Kontribusi sangat diterima! Silakan buat pull request atau issue.README.md          # Documentation
```

### Testing

Test menggunakan FastAPI Swagger UI:
```
http://localhost:8000/docs
```

## Docker Commands

Build image:
```bash
docker build -t rembg-service .
```

Run container:
```bash
docker run -p 8000:8000 rembg-service
```

Stop container:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

## Requirements

- Python 3.11+
- 2GB+ RAM (untuk model AI)
- Docker & Docker Compose (optional)

## Troubleshooting

### Model download lambat
Model AI akan didownload otomatis saat pertama kali dijalankan. Pastikan koneksi internet stabil.

### Error "libGL.so.1"
Pastikan libgl1 sudah terinstall (sudah termasuk di Dockerfile).

### Memory error
Tingkatkan memory limit Docker atau gunakan instance dengan RAM lebih besar.

## License

MIT

## Author

Dibuat dengan ❤️ untuk background removal yang cepat dan mudah
