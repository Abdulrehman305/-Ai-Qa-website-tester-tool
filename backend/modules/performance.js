// backend/modules/performance.js
const fs = require("fs");
const path = require("path");
const chromeLauncher = require("chrome-launcher");
const lighthouse = require("lighthouse");
const puppeteer = require("puppeteer");

async function analyzePerformance(targetUrl, opts = {}) {
  const {
    chromeFlags = ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
    lighthouseConfig = null,
    headless = true,
    screenshotName = "performance_screenshot.png",
  } = opts;

  // Launch Chrome for Lighthouse (chrome-launcher)
  const chrome = await chromeLauncher.launch({
    chromeFlags,
    chromePath: opts.chromePath || undefined,
  });

  const lighthouseOpts = {
    port: chrome.port,
    output: "json",
    logLevel: "info",
  };

  // Run Lighthouse (Core Web Vitals + performance metrics)
  let lhr = null;
  try {
    const runnerResult = await lighthouse(
      targetUrl,
      lighthouseOpts,
      lighthouseConfig
    );
    lhr = runnerResult.lhr;
  } catch (err) {
    console.warn("Lighthouse run failed:", err.message || err);
  }

  // Connect Puppeteer to the same Chrome instance to collect console and network data & screenshot
  const browserWSEndpoint = `http://127.0.0.1:${chrome.port}`;
  let browser;
  let page;
  const consoleMessages = [];
  let totalRequests = 0;
  let totalBytes = 0;

  try {
    // Puppeteer connect using browserURL (works with chrome-launcher)
    browser = await puppeteer.connect({
      browserURL: `http://127.0.0.1:${chrome.port}`,
    });
    page = await browser.newPage();

    // Collect console errors/warnings
    page.on("console", (msg) => {
      const type = msg.type();
      const text = msg.text();
      if (type === "error" || type === "warning") {
        consoleMessages.push({ type, text });
      }
    });

    // Track network requests and attempt to sum bytes (content-length when available)
    page.on("requestfinished", async (request) => {
      try {
        totalRequests += 1;
        const res = request.response();
        if (res) {
          const headers = res.headers() || {};
          const cl = headers["content-length"] || headers["Content-Length"];
          if (cl) {
            totalBytes += parseInt(cl, 10) || 0;
          } else {
            // If content-length not provided, try to get buffer length (may be memory heavy)
            try {
              const buf = await res.buffer();
              totalBytes += buf ? buf.length : 0;
            } catch (e) {
              // ignore buffer errors
            }
          }
        }
      } catch (e) {
        // ignore per-request errors
      }
    });

    // Navigate to page and wait for network idle
    await page.goto(targetUrl, { waitUntil: "networkidle2", timeout: 30000 });

    // Take full page screenshot
    const screenshotsDir = path.join(process.cwd(), "..", "screenshots"); // backend/../screenshots expected at project root
    try {
      fs.mkdirSync(screenshotsDir, { recursive: true });
    } catch (e) {}
    const screenshotPath = path.join(screenshotsDir, screenshotName);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    // Read screenshot and encode base64 to return in JSON (small sites OK; for very large images consider returning path instead)
    const screenshotBase64 = fs.readFileSync(screenshotPath, {
      encoding: "base64",
    });

    // Build a lightweight performance summary from LHR if present
    const perfSummary = {
      title: lhr?.requestedUrl || (await page.title?.()),
      lcp: lhr?.audits?.["largest-contentful-paint"]?.numericValue || null,
      fcp: lhr?.audits?.["first-contentful-paint"]?.numericValue || null,
      cls: lhr?.audits?.["cumulative-layout-shift"]?.numericValue || null,
      speedIndex: lhr?.audits?.["speed-index"]?.numericValue || null,
      overallScore: lhr?.categories?.performance?.score
        ? Math.round(lhr.categories.performance.score * 100)
        : null,
    };

    // Close Puppeteer page but keep chrome for proper shutdown below
    await page.close();
    page = null;

    // Kill chrome launched by chrome-launcher
    await chrome.kill();

    return {
      success: true,
      perfSummary,
      lighthouseRaw: lhr || null,
      consoleMessages,
      totalRequests,
      totalBytes,
      screenshotBase64, // base64 string (png)
      screenshotPath,
    };
  } catch (err) {
    // Ensure we kill chrome on failure
    try {
      await chrome.kill();
    } catch (e) {}
    return { success: false, error: String(err) };
  } finally {
    try {
      if (page && !page.isClosed()) await page.close();
    } catch (e) {}
    try {
      if (browser) await browser.disconnect();
    } catch (e) {}
  }
}

module.exports = { analyzePerformance };
