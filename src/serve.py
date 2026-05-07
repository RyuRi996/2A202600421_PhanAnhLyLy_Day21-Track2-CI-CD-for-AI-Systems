import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import storage

app = FastAPI(title="CI/CD AI Inference API")

# Lấy tên bucket từ biến môi trường (mặc định là tên bucket của bạn nếu không tìm thấy biến)
GCS_BUCKET = os.environ.get("GCS_BUCKET", "day-21-2a202600421")
GCS_MODEL_KEY = "models/model.pkl"  # Đường dẫn file trên GCS
MODEL_PATH = "model.pkl"           # Đường dẫn lưu file tạm trên máy chủ

def download_model():
    """Tải file model.pkl từ GCS về máy khi server khởi động."""
    print(f"Downloading model from gs://{GCS_BUCKET}/{GCS_MODEL_KEY}...")
    try:
        # Sử dụng file key để xác thực (đảm bảo file gcp-key.json đã có trên máy chủ)
        client = storage.Client.from_service_account_json("gcp-key.json")
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_MODEL_KEY)
        
        os.makedirs(os.path.dirname(MODEL_PATH) if os.path.dirname(MODEL_PATH) else ".", exist_ok=True)
        blob.download_to_filename(MODEL_PATH)
        print("Model downloaded successfully!")
    except Exception as e:
        print(f"Error downloading model: {e}")
        raise e

# Tải mô hình khi module được load
download_model()
model = joblib.load(MODEL_PATH)

class PredictionRequest(BaseModel):
    features: list

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        # Dự đoán nhãn
        prediction = model.predict([request.features])
        return {"prediction": int(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)