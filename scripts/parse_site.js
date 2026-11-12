const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

function clean(str) {
  return str.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

const judgesSection = html.match(/<section[^>]*id=["']judges["'][^>]*>([\s\S]*?)<\/section>/i);
if (judgesSection) {
  console.log('=== JUDGES LIST ===');
  // extract individual judges cards
  const judges = judgesSection[1].match(/<li[^>]*>([\s\S]*?)<\/li>|<div[^>]*class=["'][^"']*judge[^"']*["'][^>]*>([\s\S]*?)<\/div>/gi) || [];
  console.log(clean(judgesSection[1]));
}

const faqSection = html.match(/<section[^>]*id=["']faq["'][^>]*>([\s\S]*?)<\/section>/i);
if (faqSection) {
  console.log('\n=== FAQ LIST ===');
  console.log(clean(faqSection[1]));
}

const bannerSection = html.match(/<section[^>]*id=["']banner["'][^>]*>([\s\S]*?)<\/section>/i);
if (bannerSection) {
  console.log('\n=== BANNER AT A GLANCE ===');
  console.log(clean(bannerSection[1]));
}

const timelineSection = html.match(/<section[^>]*id=["']timeline["'][^>]*>([\s\S]*?)<\/section>/i);
if (timelineSection) {
  console.log('\n=== TIMELINE ===');
  console.log(clean(timelineSection[1]));
}
