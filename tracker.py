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
    all_news = []

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
            currency = "USD" if ".SR" not in symbol and symbol != "^TASI.SR" else "SAR"

            results.append({
                "name": name,
                "symbol": symbol,
                "price": f"{current_price:.2f} {currency}",
                "status": status,
                "low_52w": f"{low_52w:.2f} {currency}"
            })

            # Fetch news
            ticker_news = ticker.news
            for item in ticker_news[:3]: # Get top 3 news per ticker
                content = item.get('content', item) # Handle different yfinance versions
                all_news.append({
                    "title": content.get('title'),
                    "link": content.get('canonicalUrl', {}).get('url') or content.get('link'),
                    "publisher": content.get('provider', {}).get('displayName') or content.get('publisher'),
                    "date": content.get('pubDate') or content.get('providerPublishTime'),
                    "ticker": symbol
                })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    # Calculate ratios
    ratio_results = []
    trending_up_count = 0
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

                if ratio_val > prev_ratio:
                    trending_up_count += 1

                ratio_results.append({
                    "name": r['name'],
                    "value": f"{ratio_val:.4f}",
                    "trend": trend
                })
            else:
                print(f"Insufficient data for ratio {r['name']}")
        except Exception as e:
            print(f"Error calculating ratio {r['name']}: {e}")

    # Rotation Assessment
    if trending_up_count == len(ratios):
        rotation_status = "🚀 Violent Re-rating in Progress"
        rotation_color = "text-green-400"
    elif trending_up_count > 0:
        rotation_status = "⚖️ Mixed Signals / Early Rotation"
        rotation_color = "text-yellow-400"
    else:
        rotation_status = "😴 No Rotation Detected Yet"
        rotation_color = "text-red-400"

    # Generate HTML with Dark Mode and News
    company_cards = "".join([f"""
                <div class="bg-gray-800 p-6 rounded-xl shadow-lg border-t-4 {'border-orange-500' if 'Near Low' in r['status'] else 'border-green-500'}">
                    <h3 class="font-bold text-xl mb-2 text-white">{r['name']}</h3>
                    <p class="text-gray-300 text-3xl mb-2 font-mono">{r['price']}</p>
                    <p class="text-sm font-semibold { 'text-orange-400' if 'Near Low' in r['status'] else 'text-green-400'}">{r['status']}</p>
                    <p class="text-xs text-gray-500 mt-2">52w Low: {r['low_52w']}</p>
                </div>
    """ for r in results])

    ratio_cards = "".join([f"""
                <div class="bg-gray-800 p-6 rounded-xl shadow-lg border-l-4 border-blue-500">
                    <h3 class="font-bold text-lg mb-2 text-white">{r['name']}</h3>
                    <p class="text-gray-300 text-4xl mb-2 font-mono">{r['value']}</p>
                    <p class="text-sm font-semibold {'text-green-400' if 'Trending Up' in r['trend'] else 'text-red-400'}">{r['trend']}</p>
                    <p class="text-xs text-gray-500 mt-1">(30-day relative trend)</p>
                </div>
    """ for r in ratio_results])

    news_items = "".join([f"""
                <div class="mb-4 pb-4 border-b border-gray-700 last:border-0">
                    <span class="text-xs font-bold px-2 py-1 rounded bg-gray-700 text-gray-300 mr-2">{n['ticker']}</span>
                    <a href="{n['link']}" target="_blank" class="text-blue-400 hover:text-blue-300 font-medium">{n['title']}</a>
                    <div class="text-xs text-gray-500 mt-1">{n['publisher']} • {n['date']}</div>
                </div>
    """ for n in all_news if n['title'] and n['link']])

    html_template = f"""
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agri-Input Narrative Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #111827; }}
    </style>
</head>
<body class="text-gray-200 font-sans leading-normal tracking-normal">
    <div class="container mx-auto p-4 md:p-8">
        <header class="mb-10 flex flex-col md:flex-row justify-between items-center bg-gray-800 p-6 rounded-2xl shadow-2xl">
            <div class="text-center md:text-left">
                <h1 class="text-4xl font-extrabold text-green-500 tracking-tight">Agri-Input Narrative Tracker</h1>
                <p class="text-gray-400 mt-2 italic">Monitoring the great capital rotation into food security.</p>
            </div>
            <div class="mt-4 md:mt-0 text-right">
                <p class="text-sm text-gray-500">Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                <div class="text-xl font-bold mt-1 {rotation_color}">{rotation_status}</div>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="lg:col-span-2 space-y-8">
                <section>
                    <h2 class="text-2xl font-bold mb-6 flex items-center">
                        <span class="w-2 h-8 bg-green-500 mr-3 rounded-full"></span>
                        Company Watchlist
                    </h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {company_cards}
                    </div>
                </section>

                <section>
                    <h2 class="text-2xl font-bold mb-6 flex items-center">
                        <span class="w-2 h-8 bg-blue-500 mr-3 rounded-full"></span>
                        Rotation Ratios
                    </h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {ratio_cards}
                    </div>
                </section>
            </div>

            <aside>
                <section class="bg-gray-800 p-6 rounded-2xl shadow-xl h-full">
                    <h2 class="text-2xl font-bold mb-6 flex items-center">
                        <span class="w-2 h-8 bg-purple-500 mr-3 rounded-full"></span>
                        Agri-News Feed
                    </h2>
                    <div class="overflow-y-auto max-h-[800px] pr-2 custom-scrollbar">
                        {news_items or '<p class="text-gray-500">No recent news found.</p>'}
                    </div>
                </section>
            </aside>
        </div>

        <footer class="mt-16 pt-8 border-t border-gray-800 text-gray-600 text-center text-sm">
            Zero-cost dashboard powered by yfinance & GitHub Actions.
            <br>
            <span class="mt-2 inline-block">Betting on the 2-3 year Agri Narrative.</span>
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
