# currency-conversion-with-inflation

A python script that displays the inflation-adjusted total yearly revenue in USD per country for a given transaction file in csv format.

### Installation
- Clone the git repository, make sure to create a virutal environment and install the dependencies in the
requirements.txt file, where `x` is the desired python 3 version to be used.
```python
virtualenv --python="/usr/bin/python3.<x>" "${HOME}/.envs/myenv"
source "${HOME}/.envs/myenv/bin/activate"
pip install -r requirements.txt
```

### Usage
Run the script through the command line or your favourite IDE and specify the necessary
arguments:
- path: path to the `transaction.csv` file. Default is current directory.

```python
python calculate_inflation_adjusted_income.py --path="<path>"
```

### Output
Output will be in console in the form of a table in the suggested output format. Below are the results.




### Note
- The library used for currency conversion is [currency_converter](https://pypi.org/project/CurrencyConverter/). This library does not query exchange rates in real-time and use a [fixed currency-rates file](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip), with the [European Central Bank](https://www.ecb.europa.eu/home/html/index.en.html) being the source, which makes it faster to run. However some exchange rate for certain dates are not present, and as a workaround we try to look for the first present exchange rate in the past 5 days from the transaction date.
Another alternative is to use [forex-python](https://pypi.org/project/forex-python/) library, however that library query the exchange rates in real time and makes it slow, so for simplicity, in this task, `currency_converter` is used.
- The variable initalisation and coding/indent style used is the one we're adapting in the current job, where we prefer `snake_case` to `camelCase`. 
