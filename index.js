const express = require('express');
const path = require('path');
const app = express();
const port = 3000;

// Serve static files
app.use(express.static(path.join(__dirname, 'website')));

// Inject environment variables
app.get('/env-config.js', (req, res) => {
  res.set('Content-Type', 'application/javascript');
  res.send(`
    window.SUPABASE___SUPABASE_URL = "${process.env.SUPABASE___SUPABASE_URL}";
    window.SUPABASE___SUPABASE_ANON_KEY = "${process.env.SUPABASE___SUPABASE_ANON_KEY}";
  `);
});

// Start server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
