import requests
import pygal
from pygal.style import DarkSolarizedStyle
from datetime import datetime
import csv
from flask import Flask, render_template, request

app = Flask(__name__)

#  get stock data from Alpha Vantage
def get_stock_data(symbol, function, api_key, start_date, end_date):
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}&datatype=json'
    response = requests.get(url)

    # check if response is valid
    if response.status_code != 200:
        print(f"Error: Failed to retrieve data. HTTP Status code: {response.status_code}")
        return None
    
    data = response.json()
    
    # Debugging: Print the raw API response (optional)
    # print("API Response:", data)  # <-- Add this line to check the returned data

    # Check if the response contains the expected key
    if 'Error Message' in data:
        print(f"Error: {data['Error Message']}")
        return None
    if not data:
        print("Error: No data received from API.")
        return None

    time_series_key = list(data.keys())[-1]  # Dynamic key name (daily, weekly, etc.)
    
    # Ensure the correct time series key exists
    if time_series_key not in data:
        print(f"Error: Time series data not found for {symbol}.")
        return None
    
    stock_data = data[time_series_key]
    
    # Filter data based on start_date and end_date
    filtered_data = {date: value for date, value in stock_data.items() if start_date <= date <= end_date}
    
    if not filtered_data:
        print(f"No data available for {symbol} in the specified date range ({start_date} to {end_date}).")
        first_available_date = list(stock_data.keys())[-1]
        print(f"Try extending your date range. Earliest available data is from {first_available_date}.")
        return None
    
    return filtered_data

# Function to generate the chart with Open, High, Low, and Close prices
def create_chart(data, title, chart_type):
    if chart_type == 'Line':
        chart = pygal.Line(style=DarkSolarizedStyle)
    elif chart_type == 'Bar':
        chart = pygal.Bar(style=DarkSolarizedStyle)
    else:
        print("Invalid chart type!")
        return

    chart.title = title
    chart.x_labels = list(data.keys())

    # Extracting Open, High, Low, and Close prices from the data
    open_prices = [float(info['1. open']) for info in data.values()]
    high_prices = [float(info['2. high']) for info in data.values()]
    low_prices = [float(info['3. low']) for info in data.values()]
    close_prices = [float(info['4. close']) for info in data.values()]

    # Adding data series to the chart
    chart.add('Open', open_prices)
    chart.add('High', high_prices)
    chart.add('Low', low_prices)
    chart.add('Close', close_prices)
    
    return chart.render(is_unicode=True)

# Function to validate date input
def validate_date_input(date_text):
    try:
        return datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        print("Incorrect date format. Please use YYYY-MM-DD.")
        return None

# read the stock symbols from the CSV file
def read_stock_symbols(file_path):
    symbols = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            symbols.append(row['Symbol'])
    return symbols

# function that run the application
@app.route('/', methods=['GET', 'POST'])
def index():
    api_key = '5EW2VPXRG7XF7PWK'
    stock_symbols = read_stock_symbols('stocks.csv')
    chart = None

    if request.method == 'POST':
        symbol = request.form['symbol']
        chart_type = request.form['chart_type']
        function = request.form['function']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        stock_data = get_stock_data(symbol, function, api_key, start_date, end_date)
        if stock_data:
            chart = create_chart(stock_data, f"{symbol} Stock Prices ({start_date} to {end_date})", chart_type)

    return render_template('index.html', stock_symbols=stock_symbols, chart=chart)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
