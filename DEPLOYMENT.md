# 🚀 Deployment Guide: FarmDoctor

Follow these steps to get your FarmDoctor AI live on the web!

## 1. Backend (FastAPI)
Recommended: [Render](https://render.com) or [Railway](https://railway.app)

1. **Create a New Web Service**: Link your GitHub repository.
2. **Root Directory**: Set it to `bankend`.
3. **Environment Variables**: Add all keys from your `.env`:
   - `GROK_API_KEY`
   - `PINECONE_API_KEY`
   - `OPENWEATHER_API_KEY`
   - `ELEVENLABS_API_KEY`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

---

## 2. Frontend (React + Vite)
### Option A: Netlify (Recommended)
1. **Connect GitHub**: Log in to [Netlify](https://app.netlify.com) and click **Add new site > Import from existing project**.
2. **Site Settings**:
   - **Base directory**: `FarmDoctor-master/frontend` (or just `frontend` if your repo root is the project folder).
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
3. **Environment Variables**:
   - Go to **Site Configuration > Environment variables**.
   - Add `VITE_API_URL`: Your **Backend URL** (e.g., `https://farmdoctor-api.onrender.com`).
4. **Deploy**: Netlify will use the `netlify.toml` I just created for you!

### Option B: Vercel
1. **Import Project**: Link your GitHub repository.
2. **Framework Preset**: Select `Vite`.
3. **Root Directory**: Set it to `frontend`.
4. **Environment Variables**:
   - `VITE_API_URL`: Set this to your **Backend URL**.
5. **Deploy**: Click Deploy!

---

## 3. Post-Deployment Check
1. Open your Frontend URL.
2. Try a question—if it works, your AI is live!
3. Click the speaker icon—if it speaks, your ElevenLabs integration is perfect!

---

## 🛠️ Local Production Preview
To see how it looks in production mode locally:
```bash
# Frontend
cd frontend
npm run build
npm run preview

# Backend
cd bankend
uvicorn app:app --host 0.0.0.0 --port 8000
```
