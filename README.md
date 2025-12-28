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
└── README.md          # Documentation
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
