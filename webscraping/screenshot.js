import puppeteer from 'puppeteer';
import fs from 'fs';

const url = process.argv[2];

(async () => {
    
    // Launching Puppeteer in headless mode
    const browser = await puppeteer.launch({
        executablePath: '/snap/bin/chromium',
        headless: "new",
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-http2'] // Additional args for running in a headless environment
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 2000, height: 1200 });

    await page.goto(url, { waitUntil: 'networkidle0' });

    // Create a unique directory for each run
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const screenshotDir = `./screenshots/${timestamp}`;
    if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir, { recursive: true });
    }

    // Taking the first screenshot
    await page.screenshot({ path: `${screenshotDir}/screen1.png` });

    // Function for scrolling and taking screenshots
    let scrollHeight = await page.evaluate(() => document.body.scrollHeight);
    let viewportHeight = page.viewport().height;
    let scrollCount = Math.ceil(scrollHeight / viewportHeight);
    for (let i = 1; i < scrollCount; i++) {
        await page.evaluate(() => window.scrollBy(0, window.innerHeight));
        await new Promise(r => setTimeout(r, 1000)); // wait for scrolling to finish
        await page.screenshot({ path: `${screenshotDir}/screen${i + 1}.png` });
    }

    await browser.close();
})();
