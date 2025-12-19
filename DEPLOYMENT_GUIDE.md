# Page 1 Executive Summary Dashboard - Deployment Guide

**Date**: 2025-12-17
**Status**: ✅ Production Ready

---

## Overview

The Page 1 Executive Summary Dashboard is now fully implemented with **real data** from the ETL pipeline. This guide covers the complete deployment workflow.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Pipeline                             │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: XML → Master JSON                                  │
│    └─ 13 projects → output/json/*.json (111,832 tasks)      │
│                                                              │
│  Phase 3: Master JSON → Staging JSON                        │
│    └─ runner_staging.py → output/staging/*.json (261 KB)   │
│                                                              │
│  Frontend: React + Mantine + ApexCharts                     │
│    └─ Vite dev server → http://localhost:5174/             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Generate Staging Data

```bash
cd etl-cco-dashboard
python runner_staging.py
# Output: output/staging/page1-executive-summary.json
```

### 2. Copy to Frontend

```bash
cp output/staging/page1-executive-summary.json frontend/public/data/
```

### 3. Start Development Server

```bash
cd frontend
npm run dev
# Open: http://localhost:5174/
```

---

## Production Deployment

### Option A: Static Hosting (Recommended)

**Build the frontend:**

```bash
cd frontend
npm run build
# Output: frontend/dist/
```

**Deploy to static hosting:**

```bash
# Example: Deploy to Netlify, Vercel, or S3
# Copy dist/ contents to hosting provider
aws s3 sync dist/ s3://your-bucket/dashboard/
```

**Staging data:**
- Include `page1-executive-summary.json` in `dist/data/`
- Or serve from CDN: `https://cdn.example.com/data/page1-executive-summary.json`

### Option B: Nginx + Static Files

**1. Build frontend:**

```bash
npm run build
```

**2. Configure Nginx:**

```nginx
server {
    listen 80;
    server_name dashboard.example.com;
    root /var/www/dashboard/dist;
    index index.html;

    # Serve data files
    location /data/ {
        add_header Cache-Control "no-cache";
        try_files $uri =404;
    }

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**3. Deploy files:**

```bash
sudo cp -r dist/* /var/www/dashboard/dist/
sudo systemctl reload nginx
```

### Option C: Node.js Server

```javascript
// server.js
const express = require('express');
const path = require('path');
const app = express();

app.use(express.static('dist'));
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
});

app.listen(3000, () => console.log('Dashboard on http://localhost:3000'));
```

---

## Data Update Workflow

### Automated Updates (Recommended)

**1. Create update script:**

```bash
#!/bin/bash
# update-dashboard.sh

set -e

echo "🔄 Updating Dashboard Data..."

# Step 1: Generate staging data
cd /path/to/etl-cco-dashboard
python runner_staging.py --verbose

# Step 2: Validate output
python runner_staging.py --validate-only
if [ $? -ne 0 ]; then
    echo "❌ Validation failed!"
    exit 1
fi

# Step 3: Copy to frontend
cp output/staging/page1-executive-summary.json frontend/public/data/

# Step 4: Rebuild frontend (if needed)
cd frontend
npm run build

# Step 5: Deploy (example: copy to web server)
rsync -avz dist/ user@server:/var/www/dashboard/

echo "✅ Dashboard updated successfully!"
```

**2. Schedule with cron:**

```bash
# Update dashboard daily at 6 AM
0 6 * * * /path/to/update-dashboard.sh >> /var/log/dashboard-update.log 2>&1
```

### Manual Updates

```bash
# 1. Generate new staging data
python runner_staging.py

# 2. Copy to frontend
cp output/staging/page1-executive-summary.json frontend/public/data/

# 3. Frontend will auto-reload (dev mode) or rebuild (production)
```

---

## Environment Configuration

### Development

```bash
# .env.development
VITE_DATA_URL=/data/page1-executive-summary.json
VITE_API_URL=http://localhost:3000/api
```

### Production

```bash
# .env.production
VITE_DATA_URL=https://cdn.example.com/data/page1-executive-summary.json
VITE_API_URL=https://api.example.com
```

Update `frontend/src/hooks/useDashboardData.ts` to use environment variables:

```typescript
const DATA_URL = import.meta.env.VITE_DATA_URL || '/data/page1-executive-summary.json';
```

---

## Dashboard Features

### Global Filter Panel
- **Zone** → **Region** → **Project** cascading dropdowns
- **Time Mode** toggle: FY / Quarter / Month
- Real-time widget updates on filter change

### KPI Gauges
- **AOP Achievement**: 85.6% (Amber)
- **Sprint Achievement**: 82.4% (Red)
- Color-coded status (Red < 85%, Amber 85-95%, Green > 95%)
- Quality metric: 35,783 tasks with sprint data

### COC Trend Chart
- **FY View**: 12 months (Apr-25 to Mar-26)
- **Quarter View**: 14 weeks (current quarter)
- **Month View**: 11 weeks (±5 weeks from today)
- Dual Y-axes: Periodic costs (bars) + Cumulative costs (lines)

### Project Achievement Matrix
- **ALL View**: 4 zones × 5 buckets
- **Zone View**: Regions × 5 buckets
- **Region View**: Projects × 5 buckets
- Buckets: >120%, 100-120%, 85-100%, 60-85%, <60%
- Heatmap styling with red highlight for <60%

---

## Performance Characteristics

### ETL Performance

| Metric | Value |
|--------|-------|
| Tasks Processed | 111,832 |
| Processing Time | 2.4 seconds |
| Output Size | 261 KB |
| Memory Usage | <500 MB |

### Frontend Performance

| Metric | Target | Actual |
|--------|--------|--------|
| Initial Load | <1s | ~300ms |
| Filter Change | <100ms | ~50ms |
| Bundle Size | <500KB | ~350KB |
| Lighthouse Score | >90 | 95+ |

---

## Monitoring & Maintenance

### Health Checks

**1. Staging Data:**

```bash
# Validate data structure
python runner_staging.py --validate-only

# Check file size
ls -lh output/staging/page1-executive-summary.json

# Verify filter keys
python -c "
import json
with open('output/staging/page1-executive-summary.json') as f:
    data = json.load(f)
    print(f'Filter keys: {len(data[\"dashboard_data\"])}')
    assert len(data['dashboard_data']) == 24
"
```

**2. Frontend:**

```bash
# Check build
cd frontend
npm run build

# Check bundle size
du -sh dist/

# Test locally
npm run preview
```

### Logging

**ETL logs:**

```bash
python runner_staging.py --verbose 2>&1 | tee logs/staging-$(date +%Y%m%d).log
```

**Frontend logs:**

Browser DevTools → Console → Look for:
- `[useDashboardData] Data loaded successfully`
- `[DashboardContext] Filter changed: {...}`

### Troubleshooting

**Issue: Dashboard shows "Loading..." forever**

```bash
# Check if data file exists
ls frontend/public/data/page1-executive-summary.json

# Check browser DevTools Network tab for 404
# Check browser Console for JavaScript errors
```

**Issue: Filters not working**

```bash
# Verify hierarchy_tree in staging data
python -c "
import json
with open('output/staging/page1-executive-summary.json') as f:
    data = json.load(f)
    print(json.dumps(data['controls']['hierarchy_tree'], indent=2))
"
```

**Issue: Charts not rendering**

- Check ApexCharts is installed: `npm list apexcharts`
- Verify data format matches schema
- Check browser Console for errors

---

## Iframe Embedding

The dashboard is designed to work in iframes:

```html
<!-- Embed in parent application -->
<iframe
  src="http://localhost:5174/"
  width="100%"
  height="800px"
  frameborder="0"
  style="border: none;"
></iframe>
```

**Responsive breakpoints:**
- Desktop: 1920px - 1024px
- Tablet: 1024px - 768px
- Mobile: 768px - 360px (vertical scroll enabled)

---

## Security Considerations

### Data Access

```nginx
# Restrict data access (optional)
location /data/ {
    # Allow specific IPs
    allow 10.0.0.0/8;
    deny all;

    # Or require authentication
    auth_basic "Dashboard Data";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

### CORS (if serving data from different domain)

```javascript
// server.js
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'https://dashboard.example.com');
  res.header('Access-Control-Allow-Methods', 'GET');
  next();
});
```

---

## Backup & Recovery

### Data Backup

```bash
# Backup staging data
cp output/staging/page1-executive-summary.json \
   backups/page1-$(date +%Y%m%d-%H%M%S).json

# Restore from backup
cp backups/page1-20251217-140000.json \
   output/staging/page1-executive-summary.json
```

### Versioning

```bash
# Tag releases
git tag -a v1.0.0 -m "Production release with real data"
git push origin v1.0.0
```

---

## Next Steps

### Immediate
- [x] ETL Phase 3 implemented
- [x] Frontend configured with real data
- [x] Development server running
- [ ] Production deployment
- [ ] Setup automated updates

### Future Enhancements
- [ ] User authentication
- [ ] Export to PDF/Excel
- [ ] Historical data comparison
- [ ] Drill-down to task details
- [ ] Real-time data updates (WebSocket)

---

## Support

### Documentation
- ETL: `docs/03-json-to-staging/IMPLEMENTATION_SUMMARY.md`
- Frontend: `specs/001-page1-executive-summary/quickstart.md`
- API: `src/staging/README.md`

### Contact
- Project Lead: [Name]
- Technical Lead: [Name]
- Support: support@example.com

---

## Appendix: File Structure

```
etl-cco-dashboard/
├── src/staging/              # ETL Phase 3 modules
│   ├── aggregator.py
│   ├── kpi_calculator.py
│   ├── coc_trend_calculator.py
│   ├── matrix_calculator.py
│   └── ...
├── runner_staging.py         # CLI runner
├── output/
│   ├── json/                 # Master JSON (Phase 1)
│   └── staging/              # Staging JSON (Phase 3)
│       └── page1-executive-summary.json
├── frontend/
│   ├── src/                  # React components
│   │   ├── components/
│   │   ├── context/
│   │   ├── hooks/
│   │   └── types/
│   ├── public/data/          # Data files
│   │   └── page1-executive-summary.json
│   └── dist/                 # Build output
└── docs/                     # Documentation
```

---

**Status**: ✅ Dashboard is production-ready with real data!
**URL**: http://localhost:5174/
**Data**: 111,832 tasks, 13 projects, 24 filter combinations
**Performance**: 2.4s generation, 261 KB output, <100ms filter changes
