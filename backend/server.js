// backend/server.js
const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
import puppeteer from "puppeteer";

const browser = await puppeteer.launch({
  headless: true,
  executablePath:
    "C:\\Users\\HP\\.cache\\puppeteer\\chrome\\win64-140.0.7339.82\\chrome-win64\\chrome.exe",
  args: ["--no-sandbox", "--disable-setuid-sandbox"],
});

const { analyzePerformance } = require("./modules/performance");

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Keep the older lightweight checks (optional) — you can remove them or keep both
app.post("/run-tests", async (req, res) => {
  const { url } = req.body;
  if (!url) return res.status(400).json({ error: "URL is required" });

  const results = {
    meta: { url, startedAt: new Date().toISOString() },
  };

  try {
    // Run performance (Lighthouse + Puppeteer data)
    const perf = await analyzePerformance(url, {
      chromeFlags: ["--no-sandbox", "--disable-gpu"],
    });
    results.performance = perf;

    // You can keep or add other lightweight checks here (seo/accessibility) later.
    // Example: simple counts done via / lightweight page evaluation can be added as separate modules.

    results.completedAt = new Date().toISOString();
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
});

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Server running on port ${port}`));
