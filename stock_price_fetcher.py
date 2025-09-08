import yfinance as yf
import matplotlib.pyplot as plt
import os

# Correct ticker list
ticker_list = ["^GSPC", "AAPL"]

# Download last day (1-minute interval data)
data = yf.download(ticker_list, period="1d", interval="1m")
print(data.tail())

# Create results folder if missing
os.makedirs("results", exist_ok=True)

plt.figure(figsize=(10, 6))
plt.plot(data.index, data["Close"]["^GSPC"], label="S&P 500", linewidth=1.5)
#plt.plot(data.index, data["Close"]["AAPL"], label="Apple", linewidth=1.5)

plt.title("S&P 500 & AAPL - Intraday (1m interval)")
plt.xlabel("Time")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)

plt.savefig("results/sp500_daily.png", dpi=300, bbox_inches="tight")
plt.close()

print("Chart saved as results/sp500_daily.png")
