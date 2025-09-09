---
layout: page
title: "FX Converter + Filled Chart"
permalink: /projects/forex-converter/
description: "PyScript-based FX converter with a filled area chart vs baseline."
---

<!-- Page-scoped styles and PyScript -->
<link rel="stylesheet" href="{{ '/assets/css/forex_conv.css' | relative_url }}">
<link rel="stylesheet" href="https://pyscript.net/releases/2025.8.1/core.css">
<script type="module" src="https://pyscript.net/releases/2025.8.1/core.js"></script>

<h1>Foreign Exchange (FX) — Converter &amp; Filled Chart</h1>
<div class="card">
  <div class="grid">
    <div>
      <label for="fx-amt">Amount</label>
      <input id="fx-amt" type="number" step="any" value="1000">
    </div>
    <div>
      <label for="fx-base">From</label>
      <select id="fx-base"></select>
    </div>
    <div>
      <label for="fx-quote">To</label>
      <select id="fx-quote"></select>
    </div>
    <div>
      <label for="fx-days">Lookback (days)</label>
      <input id="fx-days" type="number" min="2" max="3650" value="180" />
    </div>
  </div>
  <button class="btn" py-click="convert">Convert &amp; Plot</button>

  <div class="result" id="fx-out"></div>
  <div class="muted" id="fx-meta"></div>
  <div id="plot"></div>
</div>

<py-config>
  packages = ["matplotlib"]
</py-config>
<py-script src="{{ '/assets/py/forex_conv.py' | relative_url }}"></py-script>
