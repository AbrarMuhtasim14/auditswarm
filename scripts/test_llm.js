const fs = require('fs');
const content = fs.readFileSync('.env.local', 'utf8');
const env = {};
content.split(/\r?\n/).forEach(l => {
  const idx = l.indexOf('=');
  if (idx !== -1) {
    const k = l.slice(0, idx).trim();
    let v = l.slice(idx + 1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
      v = v.slice(1, -1);
    }
    env[k] = v;
  }
});

let baseUrl = env.MUSE_BASE_URL.replace(/\/+$/, '');
const endpoint = baseUrl.endsWith('/chat/completions') ? baseUrl : baseUrl + '/chat/completions';
const url = new URL(endpoint);
const httpMod = url.protocol === 'https:' ? require('https') : require('http');

const body = JSON.stringify({
  model: env.MUSE_MODEL,
  messages: [{ role: 'user', content: 'Say hello in 5 words' }],
  max_tokens: 2048
});

const req = httpMod.request(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + env.MUSE_API_KEY
  }
}, res => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    try {
      const parsed = JSON.parse(data);
      console.log('Finish Reason:', parsed.choices[0].finish_reason);
      console.log('Message Content:', parsed.choices[0].message.content);
      console.log('Reasoning details:', parsed.usage.completion_tokens_details);
    } catch(e) {
      console.log(data);
    }
  });
});

req.on('error', err => {
  console.error('Request error:', err.message);
});

req.write(body);
req.end();
