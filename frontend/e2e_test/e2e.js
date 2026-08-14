import puppeteer from 'puppeteer';
import fs from 'fs';

async function run() {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  const logs = [];
  const log = (msg) => { console.log(msg); logs.push(msg); };
  page.on('console', msg => log(`[CONSOLE] ${msg.type().toUpperCase()} ${msg.text()}`));
  
  // Intercept and log API
  page.on('response', async res => {
    if (res.url().includes('/api/v1')) {
      log(`[API RES] ${res.status()} ${res.url()}`);
      if (res.status() >= 400 || res.url().includes('generate') || res.url().includes('posts')) {
        try { log(`[API BODY] ${await res.text()}`); } catch(e) {}
      }
    }
  });

  const clickByText = async (selector, text) => {
    await page.waitForSelector(selector);
    const clicked = await page.evaluate((sel, txt) => {
      const els = Array.from(document.querySelectorAll(sel));
      const el = els.find(e => e.textContent.trim().toLowerCase().includes(txt.toLowerCase()));
      if (el) { el.click(); return true; }
      return false;
    }, selector, text);
    if (!clicked) throw new Error(`Could not find ${selector} with text "${text}"`);
    await new Promise(r => setTimeout(r, 1000));
  };

  try {
    log("=== Navigating ===");
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    
    log(`URL: ${page.url()}`);
    
    // Create workspace if we are on /workspaces
    if (page.url().includes('/workspaces')) {
      log("Creating workspace...");
      await clickByText('button', 'Create Workspace');
      await page.type('input[name="name"]', 'E2E Workspace');
      await clickByText('button', 'Create');
      await page.waitForNavigation({ waitUntil: 'networkidle0' }).catch(()=>log("no nav"));
    }
    
    log("=== Navigating to Projects ===");
    await clickByText('a, button, div', 'Projects');
    
    log("Checking for 'New Project' button...");
    const newProjCreated = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const newBtn = btns.find(b => b.textContent.includes('New Project'));
      if (newBtn) { newBtn.click(); return true; }
      return false;
    });
    
    if (newProjCreated) {
      log("Creating new project...");
      await new Promise(r => setTimeout(r, 500));
      await page.type('input[name="name"]', 'E2E Project');
      await clickByText('button', 'Create Project');
      await new Promise(r => setTimeout(r, 1000));
    }
    
    log("Clicking into a project...");
    await page.evaluate(() => {
      // Find a project card or link
      const links = Array.from(document.querySelectorAll('a'));
      const projLink = links.find(l => l.href.includes('/projects/'));
      if (projLink) projLink.click();
    });
    
    await new Promise(r => setTimeout(r, 1000));
    log(`URL in project: ${page.url()}`);
    
    log("Clicking Create Post...");
    await clickByText('button, a', 'Create Post');
    
    await new Promise(r => setTimeout(r, 2000));
    log(`URL in create post: ${page.url()}`);
    
    log("Filling generation form...");
    // The form has platform, content_type, user_request, audience, tone
    await page.evaluate(() => {
      const selects = document.querySelectorAll('select');
      if (selects.length > 0) selects[0].value = 'twitter';
      if (selects.length > 1) selects[1].value = 'short_post';
      
      const textareas = document.querySelectorAll('textarea');
      if (textareas.length > 0) {
        textareas[0].value = 'Write a post about AI E2E testing';
        // Dispatch input event to trigger react state
        textareas[0].dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    
    log("Clicking Generate...");
    await clickByText('button', 'Generate');
    
    log("Waiting for generation to complete (up to 30s)...");
    await page.waitForResponse(res => res.url().includes('/generate') && res.status() === 200, { timeout: 30000 });
    
    log("Generation complete! Clicking Save Draft...");
    await new Promise(r => setTimeout(r, 1000));
    await clickByText('button', 'Save Draft');
    
    await new Promise(r => setTimeout(r, 2000));
    log(`URL after save draft: ${page.url()}`);
    
    log("Clicking Submit for Review...");
    await clickByText('button', 'Submit for Review');
    
    await new Promise(r => setTimeout(r, 2000));
    log("E2E complete!");
    
  } catch (error) {
    log(`[ERROR] ${error.message}`);
    await page.screenshot({ path: 'error.png' });
  } finally {
    fs.writeFileSync('e2e_logs.txt', logs.join('\n'));
    await browser.close();
  }
}

run();
