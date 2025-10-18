import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

class AlgoTrader:
    def __init__(self, symbol, start, end, budget=5000):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.budget = budget
        self.data = None
        self.position = False
        self.shares = 0
        self.cash = budget
        self.trades = []

    def fetch_data(self):
        print(f"Fetching data for {self.symbol}...")
        self.data = yf.download(self.symbol, start=self.start, end=self.end, auto_adjust=True)
        self.data = self.data[~self.data.index.duplicated()]
        self.data = self.data.ffill()
        print("Data fetched successfully\n")

    def compute_ma(self):
        self.data['MA50'] = self.data['Close'].rolling(50).mean()
        self.data['MA200'] = self.data['Close'].rolling(200).mean()

    def run_strategy(self):
        for i in range(1, len(self.data)):
            ma50 = self.data['MA50'].iloc[i]
            ma200 = self.data['MA200'].iloc[i]
            prev_ma50 = self.data['MA50'].iloc[i - 1]
            prev_ma200 = self.data['MA200'].iloc[i - 1]
            price = self.data['Close'].iloc[i]
            date = self.data.index[i].to_pydatetime()

            if prev_ma50 <= prev_ma200 and ma50 > ma200 and not self.position:
                qty = int(self.cash // price.item())
                if qty > 0:
                    self.shares = qty
                    self.cash -= qty * price.item()
                    self.position = True
                    self.trades.append(("BUY", date, price.item(), qty))
                    print(f"BUY {qty} shares at ${price.item():.2f} on {date.date()}")

            elif prev_ma50 >= prev_ma200 and ma50 < ma200 and self.position:
                self.cash += self.shares * price.item()
                self.trades.append(("SELL", date, price.item(), self.shares))
                print(f"SELL {self.shares} shares at ${price.item():.2f} on {date.date()}")
                self.shares = 0
                self.position = False

        if self.position:
            last_price = self.data['Close'].iloc[-1]
            last_date = self.data.index[-1].to_pydatetime()
            self.cash += self.shares * last_price.item()
            self.trades.append(("FORCE_SELL", last_date, last_price.item(), self.shares))
            print(f"Force-sold {self.shares} shares at ${last_price.item():.2f} on last day")
            self.shares = 0
            self.position = False

    def report(self):
        profit = self.cash - self.budget
        print("\n========== SUMMARY ==========")
        print(f"Initial Budget : ${self.budget}")
        print(f"Final Cash     : ${self.cash:.2f}")
        print(f"Net Profit/Loss: ${profit:.2f}")
        print("=============================")
        return profit

    def plot_chart(self):
        plt.figure(figsize=(12,6))
        plt.plot(self.data['Close'], label='Close Price', alpha=0.6)
        plt.plot(self.data['MA50'], label='50-Day MA', alpha=0.8)
        plt.plot(self.data['MA200'], label='200-Day MA', alpha=0.8)
        plt.title(f"{self.symbol} Golden Cross Strategy")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    trader = AlgoTrader("AAPL", "2018-01-01", "2023-12-31", budget=5000)
    trader.fetch_data()
    trader.compute_ma()
    trader.run_strategy()
    trader.report()
    trader.plot_chart()
