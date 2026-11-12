const fs = require('fs');
const https = require('https');

const tracks = JSON.parse(fs.readFileSync('tracks_list.json', 'utf8'));
if (!fs.existsSync('tracks')) fs.mkdirSync('tracks');

function download(track) {
  return new Promise((resolve, reject) => {
    const dest = 'tracks/' + track.name;
    const file = fs.createWriteStream(dest);
    https.get(track.download_url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, res => {
      res.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', err => {
      fs.unlink(dest, () => reject(err));
    });
  });
}

Promise.all(tracks.map(download)).then(() => {
  console.log('Successfully downloaded all ' + tracks.length + ' track prompts.');
  const files = fs.readdirSync('tracks');
  console.log('Downloaded files:', files.join(', '));
}).catch(console.error);
