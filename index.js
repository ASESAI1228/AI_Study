const express = require('express');
const path = require('path');
const app = express();
const port = 3000;

// Load environment variables from .env file
require('dotenv').config();

// Serve static files
app.use(express.static(path.join(__dirname, 'website')));

// Inject environment variables
// Serve env-config.js at the root path
app.get('/env-config.js', (req, res) => {
  res.set('Content-Type', 'application/javascript');
  // IMPORTANT: In a production environment, you should implement proper
  // authentication and authorization before exposing any credentials
  res.send(`
    // Supabase credentials should be properly secured in production
    window.SUPABASE___SUPABASE_URL = "${process.env.SUPABASE___SUPABASE_URL || ''}";
    window.SUPABASE___SUPABASE_ANON_KEY = "${process.env.SUPABASE___SUPABASE_ANON_KEY || ''}";
    
    // OpenAI API key should NEVER be exposed to the client
    // Server-side proxy should be used instead
    window.OPENAI_API_KEY = "${process.env.OPENAI_API_KEY || ''}"; // For development only
  `);
});

// Also serve env-config.js at the website path for relative imports
app.get('/website/env-config.js', (req, res) => {
  res.set('Content-Type', 'application/javascript');
  // IMPORTANT: In a production environment, you should implement proper
  // authentication and authorization before exposing any credentials
  res.send(`
    // Supabase credentials should be properly secured in production
    window.SUPABASE___SUPABASE_URL = "${process.env.SUPABASE___SUPABASE_URL || ''}";
    window.SUPABASE___SUPABASE_ANON_KEY = "${process.env.SUPABASE___SUPABASE_ANON_KEY || ''}";
    
    // OpenAI API key should NEVER be exposed to the client
    // Server-side proxy should be used instead
    window.OPENAI_API_KEY = "${process.env.OPENAI_API_KEY || ''}"; // For development only
  `);
});

// Start server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
