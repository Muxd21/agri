import yfinance as yf
import datetime
import pandas as pd
import os

# Define companies
tickers = {
    "Nutrien (NTR)": "NTR",
    "SABIC Agri (2020)": "2020.SR",
    "Ma'aden (1211)": "1211.SR",
    "Almarai (2280)": "2280.SR"
}

# Ratios to track
ratios = [
    {"name": "NTR / QQQ (Agri vs US Tech)", "numerator": "NTR", "denominator": "QQQ"},
    {"name": "SABIC Agri / TASI (Agri vs Saudi Market)", "numerator": "2020.SR", "denominator": "^TASI.SR"}
]

def get_data():
    results = []
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            if hist.empty:
                print(f"No data for {symbol}")
                continue

            current_price = hist['Close'].iloc[-1]
            low_52w = hist['Low'].min()
            status = "🔥 Near Low" if current_price < (low_52w * 1.1) else "✅ Trading"
            currency = "USD" if ".SR" not in symbol and symbol != "^TASI" else "SAR"

            results.append({
                "name": name,
                "symbol": symbol,
                "price": f"{current_price:.2f} {currency}",
                "status": status,
                "low_52w": f"{low_52w:.2f} {currency}"
            })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    # Calculate ratios
    ratio_results = []
    for r in ratios:
        try:
            num_ticker = yf.Ticker(r['numerator'])
            den_ticker = yf.Ticker(r['denominator'])

            num_hist = num_ticker.history(period="1mo")
            den_hist = den_ticker.history(period="1mo")

            if not num_hist.empty and not den_hist.empty:
                num_price = num_hist['Close'].iloc[-1]
                den_price = den_hist['Close'].iloc[-1]
                ratio_val = num_price / den_price

                # Simple trend check (comparing to 1 month ago)
                prev_num_price = num_hist['Close'].iloc[0]
                prev_den_price = den_hist['Close'].iloc[0]
                prev_ratio = prev_num_price / prev_den_price
                trend = "📈 Trending Up" if ratio_val > prev_ratio else "📉 Trending Down"

                ratio_results.append({
                    "name": r['name'],
                    "value": f"{ratio_val:.4f}",
                    "trend": trend
                })
            else:
                print(f"Insufficient data for ratio {r['name']}")
        except Exception as e:
            print(f"Error calculating ratio {r['name']}: {e}")

    # Generate HTML with Tailwind CSS
    company_cards = "".join([f"""
                <div class="bg-white p-6 rounded-lg shadow-md border-t-4 {'border-orange-500' if 'Near Low' in r['status'] else 'border-green-500'}">
                    <h3 class="font-bold text-xl mb-2">{r['name']}</h3>
                    <p class="text-gray-700 text-3xl mb-2 font-mono">{r['price']}</p>
                    <p class="text-sm font-semibold { 'text-orange-600' if 'Near Low' in r['status'] else 'text-green-600'}">{r['status']}</p>
                    <p class="text-xs text-gray-500 mt-2">52w Low: {r['low_52w']}</p>
                </div>
    """ for r in results])

    ratio_cards = "".join([f"""
                <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
                    <h3 class="font-bold text-lg mb-2">{r['name']}</h3>
                    <p class="text-gray-700 text-4xl mb-2 font-mono">{r['value']}</p>
                    <p class="text-sm font-semibold {'text-green-600' if 'Trending Up' in r['trend'] else 'text-red-600'}">{r['trend']}</p>
                    <p class="text-xs text-gray-400 mt-1">(Compared to 30 days ago)</p>
                </div>
    """ for r in ratio_results])

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agri-Input Narrative Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 font-sans leading-normal tracking-normal">
    <div class="container mx-auto p-8">
        <header class="mb-8 text-center md:text-left">
            <h1 class="text-4xl font-bold text-green-700">Agri-Input Narrative Tracker</h1>
            <p class="text-gray-600">Last Update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        </header>

        <section class="mb-12">
            <h2 class="text-2xl font-semibold mb-6 border-b-2 border-green-500 pb-2">Company Status</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {company_cards}
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-semibold mb-6 border-b-2 border-blue-500 pb-2">"Rotation" Signals (Ratio Tracker)</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {ratio_cards}
            </div>
        </section>

        <footer class="mt-12 pt-8 border-t text-gray-500 text-center text-sm">
            Automated via GitHub Actions. Data from Yahoo Finance.
            <br>
            Rotation indicators compare current price ratios to 30 days ago.
        </footer>
    </div>
</body>
</html>
    """

    with open("index.html", "w") as f:
        f.write(html_template)
    print("Dashboard generated successfully.")

if __name__ == "__main__":
    get_data()
