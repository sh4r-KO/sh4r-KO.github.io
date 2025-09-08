import yfinance as yf
import matplotlib.pyplot as plt

# Download last 6 months of daily data for S&P 500
data = yf.download("^GSPC", period="6mo", interval="1d")

plt.figure(figsize=(10, 6))
plt.plot(data.index, data["Close"], label="S&P 500", linewidth=1.5)
plt.title("S&P 500 Daily Closing Price (Last 6 Months)")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)

plt.savefig("results/sp500_daily.png", dpi=300, bbox_inches="tight")
plt.close()

print("Chart saved as sp500_daily.png")
