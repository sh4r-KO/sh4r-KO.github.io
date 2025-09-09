import io, base64, math
import matplotlib.pyplot as plt
from datetime import date, timedelta
from js import document, fetch

CURRENCIES = ["USD","EUR","GBP","JPY","AUD","CAD","CHF","CNY","SEK","NZD","MXN","SGD","HKD","NOK","KRW","TRY","INR","BRL","ZAR","AED","SAR","PLN","TWD","THB","DKK","MYR","IDR","PHP","CZK","HUF","ILS","CLP"]

def _fill_currency_selects():
    base = document.getElementById("fx-base")
    quote = document.getElementById("fx-quote")
    options = "".join([f'<option value="{c}">{c}</option>' for c in CURRENCIES])
    base.innerHTML = options
    quote.innerHTML = options
    base.value = "USD"
    quote.value = "EUR"

def _read_inputs():
    amt_raw = document.getElementById("fx-amt").value
    base = document.getElementById("fx-base").value
    quote = document.getElementById("fx-quote").value
    days_raw = document.getElementById("fx-days").value
    try:
        amt = float(amt_raw)
        days = int(days_raw)
        if amt <= 0 or days < 2:
            raise ValueError
    except Exception:
        return None, None, None, None
    return amt, base, quote, days

async def _fetch_timeseries(base, quote, start_s, end_s):
    # Frankfurter API: no key required
    url = f"https://api.frankfurter.dev/v1/{start_s}..{end_s}?base={base}&symbols={quote}"
    # alt: "https://api.frankfurter.app/timeseries?start={start}&end={end}&from={base}&to={quote}"

    r = await fetch(url)
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status}")
    data = await r.json()
    # data: {"amount":1.0,"base":"USD","start_date":"YYYY-MM-DD","end_date":"YYYY-MM-DD","rates":{"YYYY-MM-DD":{"EUR":x},...}}
    py = data.to_py()
    rates = py.get("rates", {})
    # Sort by date
    items = sorted(rates.items(), key=lambda kv: kv[0])
    xs = [d for d,_ in items]
    ys = [vals.get(quote) for _, vals in items]
    # filter None
    xs2, ys2 = [], []
    for d, v in zip(xs, ys):
        if isinstance(v, (int, float)) and math.isfinite(v):
            xs2.append(d); ys2.append(float(v))
    if len(xs2) < 2:
        raise RuntimeError("Not enough rate data")
    return xs2, ys2

def _embed_plot(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    img_html = f'<img src="data:image/png;base64,{data}" style="max-width:100%; border-radius:10px;" />'
    document.getElementById("plot").innerHTML = img_html

async def convert(event=None):
    loading = document.getElementById("loading")
    loading.style.display = "block"
    try:
        amt, base, quote, days = _read_inputs()
        out = document.getElementById("fx-out")
        meta = document.getElementById("fx-meta")
        if any(v is None for v in (amt, base, quote, days)):
            out.innerHTML = '<span class="warn">Enter a positive amount and a lookback of at least 2 days.</span>'
            meta.textContent = ""
            document.getElementById("plot").innerHTML = ""
            return
        if base == quote:
            out.innerHTML = '<span class="warn">Base and quote currencies must differ.</span>'
            meta.textContent = ""
            document.getElementById("plot").innerHTML = ""
            return

        # compute dates
        end = date.today()
        start = end - timedelta(days=days)
        start_s = start.isoformat()
        end_s = end.isoformat()

        try:
            xs, rates = await _fetch_timeseries(base, quote, start_s, end_s)
        except Exception as e:
            out.innerHTML = f'<span class="err">Failed to fetch rates: {e}</span>'
            meta.textContent = ""
            document.getElementById("plot").innerHTML = ""
            return

        # Value series (amount converted each day)
        values = [amt * r for r in rates]
        baseline_rate = rates[0]
        baseline_value = amt * baseline_rate

        # Build component series:
        # - baseline series: constant (baseline_value) for fill reference
        # - delta series: value - baseline_value (can be positive or negative)
        deltas = [v - baseline_value for v in values]

        # Summary for last day
        final_value = values[-1]
        change_abs = final_value - baseline_value
        change_pct = (change_abs / baseline_value) * 100 if baseline_value != 0 else 0

        color = "#34d399" if change_abs >= 0 else "#ef4444"

        out.innerHTML = (
            f"<b>{amt:,.2f} {base}</b> was worth "
            f"<b>{values[-1]:,.2f} {quote}</b> on {xs[-1]}<br>"
            f"Baseline (first day {xs[0]} @ {baseline_rate:.6f}): "
            f"<b>{baseline_value:,.2f} {quote}</b><br>"
            f'Change vs baseline: '
            f'<b style=\"color:{color}\">{change_abs:,.2f} {quote} ({change_pct:+.2f}%)</b>'
        )
        meta.textContent = f"Source: frankfurter.app • Window: {xs[0]} → {xs[-1]} • Points: {len(xs)}"

        # ---- Plot: filled baseline + gains/losses (green above, red below) ----
        X = list(range(len(xs)))
        y_baseline = [baseline_value] * len(values)
        y_actual = values

        fig = plt.figure(figsize=(7.2, 4.2))
        ax = fig.gca()

        # Fill baseline area (principal-equivalent) lightly
        ax.fill_between(X, 0, y_baseline, alpha=0.25, color="#60a5fa", label="Baseline value")

        # Positive deltas
        pos = [max(0.0, d) for d in deltas]
        if any(p > 0 for p in pos):
            ax.fill_between(X, y_baseline, [b+p for b, p in zip(y_baseline, pos)],
                            where=[p>0 for p in pos], alpha=0.6, color="#34d399", label="Gain vs baseline")

        # Negative deltas
        neg = [min(0.0, d) for d in deltas]
        if any(n < 0 for n in neg):
            ax.fill_between(X, y_baseline, [b+n for b, n in zip(y_baseline, neg)],
                            where=[n<0 for n in neg], alpha=0.5, color="#ef4444", label="Loss vs baseline")

        ax.plot(X, y_actual, linewidth=1.5)  # outline of actual value
        ax.set_title(f"{amt:,.0f} {base} in {quote} over time")
        ax.set_ylabel(f"Value in {quote}")
        ax.set_xlabel("Date")

        step = max(1, len(xs)//6)
        xticks = list(range(0, len(xs), step))
        ax.set_xticks(xticks)
        ax.set_xticklabels([xs[i] for i in xticks], rotation=30, ha="right")
        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)

        _embed_plot(fig)
    finally:
        loading.style.display = "none"

# Initialize selects on load
_fill_currency_selects()
