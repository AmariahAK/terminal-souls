# 🚀 Deploying Terminal Souls to Render

## Prerequisites
- GitHub account
- Render account (free tier available)

## Deployment Steps

### 1. Push to GitHub
```bash
# Make sure all files are committed
git add .
git commit -m "Terminal Souls - Complete overhaul with turn-based combat and adaptive AI"
git push origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `AmariahAK/terminal-souls`
4. Configure the service:
   - **Name**: `terminal-souls`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 app:app`
   - **Plan**: Free (sufficient for the game)

### 3. Environment Variables (Optional)
- `SECRET_KEY`: Set a random secret key for Flask sessions
- `PORT`: Will be set automatically by Render

### 4. Access Your Game
- Render will provide a URL like: `https://terminal-souls.onrender.com`
- The game will be playable in any web browser
- Full terminal experience with real-time input/output

## Local Testing Before Deploy
```bash
# Test the web interface locally
python app.py

# Visit http://localhost:10000 in your browser
```

## Troubleshooting

### Common Issues
- **Build fails**: Check that all dependencies are in requirements.txt
- **Game crashes**: Monitor logs in Render dashboard
- **Input lag**: Expected on free tier, upgrade for better performance

### Performance Notes
- Free tier has some limitations (spinning down after inactivity)
- For production use, consider upgrading to paid tier
- PyTorch CPU inference works well on Render's free tier

## Monitoring
- Check Render dashboard for logs and metrics
- Monitor memory usage (game uses PyTorch neural networks)
- Free tier has 512MB RAM limit - sufficient for Terminal Souls

---

**The Entity adapts to web deployment. Your patterns are now globally observable.**
