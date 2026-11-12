const fs = require('fs');
const files = fs.readdirSync('tracks').sort();

for (const f of files) {
  const content = fs.readFileSync('tracks/' + f, 'utf8');
  console.log(`\n================== ${f} ==================`);
  console.log(content.trim());
}
