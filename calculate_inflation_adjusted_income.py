import argparse
import datetime
import dateutil

import pandas as pd
import numpy as np
import cpi
from currency_converter import CurrencyConverter, ECB_URL, currency_converter


# Pandas config param to display all dataframe columns in console
pd.options.display.width = 0

"""
    Callable for converting transaction dataframe amounts into target currency.
    If the amount value is NaN, or no exchange rate is found over the past
    5 days from the transaction date, 0.0 is returned. However in this 
    assessment, those corner case aren't reached and a non-zero value is always
    returned instead.
    
    Args:
        entry: dataframe row
        converter: CurrencyConverter object
        target: target currency

    Returns:
        converted amount
"""


def convert(entry, converter, target='USD'):
    if entry.currency == target:
        return entry.amount
    else:
        date = dateutil.parser.parse(entry.processed_at).date()
        for i in range(0, 5):
            try:
                return round(converter.convert(
                        entry.amount,
                        entry.currency,
                        target,
                        date=date - datetime.timedelta(days=i),
                    ), 2)
            except currency_converter.RateNotFoundError:
                continue
        return 0.00


def main(args):
    # Load csv file, specify a fixed dtype when applicable for less memory
    # consumption
    # Note: specifying float dtype will result in amount numbers being
    # expressed in more than 2 digits as they were originally stored, for
    # simplicity, no dtype will be specified for amount column and
    # round function will be used in all amount operations.
    transaction_file = pd.read_csv(
        args.path,
        index_col='id',
        dtype={'customer_country_code': 'category',
               'currency': 'category'},
    )

    # Some rows have Null values for amount, drop them
    transaction_file.dropna(inplace=True)

    # Create a currency mapper
    currency_mapper = dict.fromkeys(
        transaction_file['currency'].value_counts().keys()
    )
    for key in currency_mapper.keys():
        if key[0].lower() == 'u' or key == '$':
            currency_mapper[key] = "USD"
        elif key[0].lower() == 'e' or key == '€':
            currency_mapper[key] = "EUR"
        else:
            currency_mapper[key] = "GBP"

    # Map currencies to a unified value
    transaction_file['currency'].replace(
        currency_mapper, inplace=True
    )

    # Convert amounts to USD
    converter = CurrencyConverter(ECB_URL)
    transaction_file['amount'] = transaction_file.apply(
        convert,
        args=(converter,),
        axis=1,
    )
    transaction_file['currency'] = 'USD'

    # Adjust values for inflation
    cpi.update()
    transaction_file['amount'] = transaction_file.apply(
        lambda row: round(cpi.inflate(
            row['amount'],
            dateutil.parser.parse(row.processed_at).date(),
        ), 2),
        axis=1,
    )

    # Add year column for an easier grouping
    transaction_file['year'] = transaction_file['processed_at'].apply(
        lambda date: dateutil.parser.parse(date).date().year
    )
    result = pd.pivot_table(
        transaction_file, values='amount', columns='year',
        index=['customer_country_code'], aggfunc=np.sum
    )
    print(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Reads a transaction file and output an inflation '
                    'adjusted total yearly revenue in USD per country.'
    )

    parser.add_argument(
        '--path',
        type=str,
        default='./transactions.csv',
        help='Path to the transaction file, in csv format.'
    )

    args = parser.parse_args()
    main(args)
