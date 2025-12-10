# GitHub Pages Deployment Guide

## ✅ Step 1: Enable GitHub Pages

Your files have been pushed to GitHub. Now you need to enable GitHub Pages:

1. Go to your repository on GitHub: https://github.com/MikeZhang69/Market-Indices-Analysis
2. Click on **Settings** (top menu bar)
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select:
   - **Branch**: `main`
   - **Folder**: `/ (root)`
5. Click **Save**

## ⏳ Step 2: Wait for Deployment

GitHub Pages will take 1-2 minutes to build and deploy your site. You'll see a message like:
> "Your site is live at https://mikezhang69.github.io/Market-Indices-Analysis/"

## 🌐 Step 3: Access Your Site

Once deployed, your site will be available at:
**https://mikezhang69.github.io/Market-Indices-Analysis/**

Or if you have a custom domain:
**https://mikezhang69.github.io/Market-Indices-Analysis/index.html**

## 📝 Notes

- GitHub Pages automatically serves `index.html` as the default page
- All image files (PNG charts) are already in the repository
- The interactive chart (`normalized_performance.html`) is also included
- Changes pushed to the `main` branch will automatically update the site

## 🔄 Updating the Site

To update your site:
1. Make changes to `index.html` or other files
2. Commit and push to the `main` branch:
   ```bash
   git add .
   git commit -m "Update web page"
   git push origin main
   ```
3. GitHub Pages will automatically rebuild (usually within 1-2 minutes)

## 🎨 Custom Domain (Optional)

If you want to use a custom domain:
1. Go to Settings → Pages
2. Enter your custom domain in the "Custom domain" field
3. Follow GitHub's instructions for DNS configuration

## ✅ Verification Checklist

- [x] Files pushed to GitHub
- [x] All required images are in the repository
- [ ] GitHub Pages enabled in repository settings
- [ ] Site is accessible at the GitHub Pages URL

---

**Your site is ready to share with the world!** 🚀

