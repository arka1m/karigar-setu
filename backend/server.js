const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
app.use(express.json());
app.use(cors());
app.use(helmet());

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'Karigar Setu Express Backend v3' });
});

// Mock Endpoints for Node.js REST API
app.get('/api/products', (req, res) => {
  res.json({ success: true, products: [] });
});

app.get('/api/artisans', (req, res) => {
  res.json({ success: true, artisan: { name: 'Ramesh Prajapati', region: 'Bankura' } });
});

app.get('/api/admin/metrics', (req, res) => {
  res.json({ success: true, metrics: { total_artisans: 1420, active_listings: 5890, total_sales: 1245000 } });
});

const PORT = process.env.PORT || 5002;
app.listen(PORT, () => {
  console.log(Karigar Setu Express Backend running on port );
});
