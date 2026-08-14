import puppeteer from 'puppeteer';
import fs from 'fs';

async function run() {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5173/projects', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 2000));
    
    // Evaluate to find project cards
    const projects = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('a')).map(a => a.href);
    });
    console.log("Found links:", projects);
    
    const html = await page.content();
    fs.writeFileSync('projects_dom.html', html);
    
  } finally {
    await browser.close();
  }
}
run();
