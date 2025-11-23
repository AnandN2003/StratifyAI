# React Landing Page Setup 🚀

## What's Changed

I've created a professional React landing page that replaces the Streamlit landing page!

### New Structure

```
StratifyAI/
├── frontend/              # React landing page
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   ├── App.css       # Styles
│   │   ├── index.js      # React entry point
│   │   └── index.css     # Global styles
│   ├── public/
│   │   └── index.html    # HTML template
│   ├── package.json      # Dependencies
│   ├── Dockerfile        # React production build
│   └── nginx.conf        # Nginx config
├── app/                  # Streamlit backend
└── docker-compose.yml    # Updated for both services
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
docker-compose up --build
```

This starts:
- **React Frontend** on http://localhost:3000 (Landing page)
- **Streamlit Backend** on http://localhost:8501 (Chat interface)

### Option 2: Development Mode

**Terminal 1 - React:**
```bash
cd frontend
npm install
npm start
```
Opens on http://localhost:3000

**Terminal 2 - Streamlit:**
```bash
docker-compose up backend
```
Or:
```bash
streamlit run app/pages/chat.py --server.port=8501
```

## 🎨 Features

### Modern React Landing Page
- ✅ Smooth animations and transitions
- ✅ Responsive design (mobile-friendly)
- ✅ Beautiful gradient hero section
- ✅ Feature cards with hover effects
- ✅ Testimonials section
- ✅ Fast and lightweight
- ✅ Production-ready with Nginx

### Flow
1. User visits http://localhost:3000 (React landing)
2. Clicks "Get Started" button
3. Redirects to http://localhost:8501 (Streamlit chat)
4. Full research functionality

## 🛠️ Customization

### Change Colors
Edit `frontend/src/App.css`:
```css
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Update Content
Edit `frontend/src/App.js` to change:
- Hero text
- Features
- Testimonials
- Button text

### Add Features
```bash
cd frontend
npm install <package-name>
```

## 📦 Build for Production

The Docker setup automatically builds an optimized production bundle using:
- Multi-stage build
- Nginx for serving
- Gzip compression
- Optimized assets

## 🔧 Troubleshooting

### Port Already in Use
Change ports in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Frontend
  - "8502:8501"  # Backend
```

### Frontend Won't Connect to Backend
Make sure both containers are running:
```bash
docker-compose ps
```

### Hot Reload in Development
Run frontend in dev mode:
```bash
cd frontend
npm start
```
Changes auto-reload!

## 🎯 Advantages Over Streamlit Landing

1. **Performance** - React is faster and more lightweight
2. **Customization** - Full control over design and interactions
3. **Animations** - Smooth, professional animations
4. **SEO** - Better for search engines
5. **Mobile** - Better mobile responsiveness
6. **Modern** - Uses latest web technologies

## 📝 Next Steps

1. ✅ Test the full flow
2. Customize colors/branding
3. Add Google Analytics
4. Add contact form
5. Deploy to production

---

**Access your app:**
- React Landing: http://localhost:3000 ⚡
- Streamlit Chat: http://localhost:8501 🤖
