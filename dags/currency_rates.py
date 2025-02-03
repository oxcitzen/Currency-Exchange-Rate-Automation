import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def run_currency_api(**kwargs):

    def get_currency_data(date_str):
        url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date_str}/v1/currencies/myr.json"
        response = requests.get(url)
        return response.json()


    current_date = datetime.now()
    dates = [current_date - timedelta(weeks=i) for i in range(4)]
    formatted_dates = [date.strftime("%Y-%m-%d") for date in dates]


    data = {date: get_currency_data(date) for date in formatted_dates}


    def converter(curr_dict):
        curr_lst = []
        
        currency = ["usd", "gbp", "eur",  "sgd", "aud", "cny"] 

        for m in currency:
            curr_lst.append(1 / curr_dict['myr'][m])
        
        curr_lst.append(1/curr_dict['myr']['thb']* 10)
        curr_lst.append(1/curr_dict['myr']['twd']* 10) 
        curr_lst.append(1/curr_dict['myr']['jpy']* 100) 
        curr_lst.append(1/curr_dict['myr']['krw']* 1000)
        
        return curr_lst


    rates = {date: converter(data[date]) for date in formatted_dates}
    df = pd.DataFrame(rates, index=["1 USD", "1 GBP", "1 EUR", "1 SGD", "1 AUD", "1 CNY", "10 THB", "10 TWD", "100 JPY", "1000 KRW"])


    # Create a line plot for each currency
    plt.figure(figsize=(10, 6))
    for i, currency in enumerate(df.index):
        plt.plot(df.columns, df.iloc[i], marker='o', label=currency)


    plt.xlabel('Date')
    plt.ylabel('Rate in MYR')
    plt.title('Currency Rates in MYR over the Last 4 Weeks')
    plt.xticks(rotation=45)  
    plt.legend(title="Currency", bbox_to_anchor=(1.05, 1), loc='upper left')


    plt.tight_layout()
    #plt.show()

    plt.savefig('/usr/local/airflow/store_files_airflow/currency_rates_graph.png', bbox_inches='tight')


    df = df.T.reset_index().melt(id_vars=["index"], var_name="currency", value_name="rate")
    df.columns = ["date", "currency", "rate"]

    # Reorder columns so 'currency' comes first and 'date' comes last
    df = df[["currency", "rate", "date"]]
    


    df.to_csv("/usr/local/airflow/store_files_airflow/currency_rates.csv" , index=False)
    
if __name__ == "__main__":
    run_currency_api()
