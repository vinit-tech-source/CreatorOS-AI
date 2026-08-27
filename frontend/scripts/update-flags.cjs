const fs = require('fs');
const { getCode } = require('country-list');
const filePath = './src/constants/countryPlatforms.ts';
let content = fs.readFileSync(filePath, 'utf8');

const customCodes = {
  'Global (Default)': 'un',
  'Russia': 'RU',
  'South Korea': 'KR',
  'Taiwan': 'TW',
  'UAE': 'AE',
  'Czechia': 'CZ'
};

const regex = /\{ country: "([^"]+)", flag: "([^"]+)", platforms: (\[.*?\]) \}/g;
const newContent = content.replace(regex, (match, country, flag, platforms) => {
  let code = customCodes[country] || getCode(country);
  if (!code) {
    console.log('No code for:', country);
    code = 'unknown';
  }
  return `{ country: "${country}", flag: "${flag}", code: "${code.toLowerCase()}", platforms: ${platforms} }`;
});

const interfaceRegex = /export interface CountryPlatformData \{[\s\S]*?\}/;
const newInterface = `export interface CountryPlatformData {
  country: string;
  flag: string;
  code: string;
  platforms: string[];
}`;

fs.writeFileSync(filePath, newContent.replace(interfaceRegex, newInterface));
console.log('Updated countryPlatforms.ts successfully');
