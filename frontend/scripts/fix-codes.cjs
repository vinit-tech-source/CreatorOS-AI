const fs = require('fs');
const filePath = './src/constants/countryPlatforms.ts';
let content = fs.readFileSync(filePath, 'utf8');
const fixes = {
  'United States': 'us',
  'Philippines': 'ph',
  'Vietnam': 'vn',
  'Turkey': 'tr',
  'United Kingdom': 'gb',
  'Netherlands': 'nl',
  'Laos': 'la',
  'Dominican Republic': 'do'
};
for (const [country, code] of Object.entries(fixes)) {
  const regex = new RegExp(`\\{ country: "${country}", flag: "[^"]+", code: "unknown"`, 'g');
  content = content.replace(regex, match => match.replace('unknown', code));
}
fs.writeFileSync(filePath, content);
console.log('Fixed unknown codes');
