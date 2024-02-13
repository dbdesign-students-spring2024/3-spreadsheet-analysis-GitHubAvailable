# Spreadsheet Analysis

<style>
    .center {
        display: block;
        margin: auto;
        margin-bottom: 10pt;
        width: 75%;
    }
</style>

A little assignment to practice finding data, munging it, and analyzing it in a spreadsheet program.

Replace the contents of this file with a report, as described in the [instructions](./instructions.md).

## 1. Dataset Details
This analysis used [data](https://www.nasdaq.com/market-activity/stocks/screener) of "Global Select" section from Nasdaq screener, *a dataset that contains the stock price, market cap (i.e., market value), as well as other basic information about selected stocks all over the world*. The original data was downloaded in **CSV** at Feb 06, 2024. Here is a preview (records 350-370, as it best captures the problem in the dataset)of the downloaded [dataset](./data/nasdaq_screener_20240206.csv):
<!-- insert data here. add -->
| **Symbol** | **Name** | **Last Sale** | **Net Change** | **% Change** | **Market Cap**  | **Country** | **IPO Year** | **Volume** |**Sector** | **Industry** |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| CORZ | Core Scientific Inc. Common Stock | $3.14 | 0.16 | 5.369% | 1212107830.00 | United States |  | 2675267 |  |  |
| CORZW | Core Scientific Inc. Tranche 1 Warrants | $1.2891 | 0.0691 | 5.664% | 0.00 | United States |  | 376112 |  |  |
| CORZZ | Core Scientific Inc. Tranche 2 Warrants | $2.58 | 0.01 | 0.389% | 995935733.00 | United States |  | 377132 |  |  |
| COST | Costco Wholesale Corporation Common Stock | $711.16 | 1.68 | 0.237% | 315634328413.00 | United States |  | 2276889 | Consumer Discretionary | Department/Specialty Retail Stores |
| CPIX | Cumberland Pharmaceuticals Inc. Common Stock | $1.97 | -0.06 | -2.956% | 28083729.00 | United States | 2009 | 6675 | Health Care | Biotechnology: Pharmaceutical Preparations |
| CPLP | Capital Product Partners L.P. Common Units | $18.03 | -0.165 | -0.907%  | 992355748.00 | Greece | 2007 | 118487 | Consumer Discretionary | Marine Transportation |
| CPRT | Copart Inc. (DE) Common Stock | $49.99 | -0.04 | -0.08% | 48001969786.00 | United States | 1994 | 4520421 | Consumer Discretionary | Other Specialty Stores |
| CPSI | Computer Programs and Systems Inc. Common Stock | $9.63 | -0.35 | -3.507% | 140104713.00 | United States | 2002 | 165123 | Technology | EDP Services |
| CPZ | Calamos Long/Short Equity & Dynamic Income Trust Common Stock | $15.09 | -0.0522 | -0.345% | 296249807.00 | United States | 2019 | 47999 | Finance | Trusts Except Educational Religious and Charitable |
| CRAI | CRA International Inc. Common Stock | $107.64 | 1.20 | 1.127%  | 753664710.00 | United States | 1998 | 35203 | Consumer Discretionary | Other Consumer Services |
| CRBU | Caribou Biosciences Inc. Common Stock | $6.76 | 0.03 | 0.446% | 597794479.00 | United States | 2021 | 1170209 | Health Care | Medicinal Chemicals and Botanical Products |
| CRCT | Cricut Inc. Class A Common Stock | $5.30 | -0.03 | -0.563% | 1161585211.00   | United States | 2021 | 543366 | Industrials | Wholesale Distributors |
| CRDO | Credo Technology Group Holding Ltd Ordinary Shares | $21.31 | -0.54 | -2.471% | 3210550663.00 | United States | 2022 | 2016250 | Technology | Semiconductors |
| CRESY | Cresud S.A.C.I.F. y A. American Depositary Shares | $8.89 | -0.47 | -5.021% | 532780047.00 | Argentina | 1997 | 333111 | Finance | Real Estate |
| CRGX | CARGO Therapeutics Inc. Common Stock | $22.05 | -1.45 | -6.17% | 908573381.00 | United States | 2023 | 194107 |  |  |
| CRMT | America's Car-Mart Inc Common Stock | $62.29 | 0.04 | 0.064% | 398209879.00 | United States |  | 145330 | Consumer Discretionary | Retail-Auto Dealers and Gas Stations |
| CRNC | Cerence Inc. Common Stock | $20.00 | -0.39 | -1.913% | 824749780.00 | United States |  | 397076     | Technology | EDP Services |
| CRNT | Ceragon Networks Ltd. Ordinary Shares | $2.45 | 0.02 | 0.823% | 206682000.00 | Israel |  | 412571     | Technology | Radio And Television Broadcasting And Communications Equipment |
| CRNX | Crinetics Pharmaceuticals Inc. Common Stock | $37.67 | 0.59 | 1.591%  | 2516328011.00 | United States | 2018 | 400599 | Health Care | Biotechnology: Pharmaceutical Preparations |
| CROX | Crocs Inc. Common Stock | $96.21 | -1.97 | -2.007% | 5827114799.00 | United States | 2006 | 922048 | Consumer Discretionary | Shoe Manufacturing |

Notice that "IPO Year," "Sector," and "Industry" columns contain empty entries and the stock with symbol "CORZW" that has a nonzero stock price and volume but with 0 market cap. The same problem also frequently occurs in other rows of the dataset.

Since a nonzero stock price indicate the stock issuer is valued by some buyers in the market, its issuer should have nonzero market cap. In addition, by the assumption that all stocks in this dataset are available for trading (i.e., has nonzero stock price), all stocks with zero market cap are considered invalid and was removed. This is accomplished by defining a testing function `_is_positive`, which is passed to the function `munge_csv`
and called as `Callable` object `is_valid` when checking given key of the CSV file as valid:
```Python
# Definition of `_is_positive`.
def _is_positive(entry : str) -> bool:
    try:
        return float(entry) > 0
    except Exception:
        return False
```
```Python
# Check if required data is valid, fix if needed.
for (key, is_valid) in req_keys.items():
    # Get index or the given key.
    index = filtered_header[key]

    # Determine if the row should be kept.
    if is_valid(row[index]):
        continue
    if not fix or key not in default_fill:
        invalid_word = True
        break
                
    # Fix invalid data.
    row[index] = default_fill[key]
```

For records with empty entries, since the data for each stock is independent from each other, these missing entries are filled with string `"Unknown"` using `munge_csv` function:
```Python
# Fill in default value.
for key in default_fill:
    # Get index or the given key.
    index = filtered_header[key]

    if row[index] == "":
        row[index] = default_fi[key]
```


## 2. Analysis
### 2.1 Aggregate Statistics
- **Max Market Cap of Each Sector**: This statitics calculates the maximum market cap for stocks from each sectors using the `MAXIFS` function with only one citeria (since `MAXIF` is not available in my mac). It shows that the largest market cap comes from the technology sector ($3,014,156,456,294.00), followed by customer discretionary sector ($1,769,074,907,670.00), while the finance sector surprisingly has a relatively small value ($73,733,761,344.00).
- **Average Market Cap of Each Sector**: This statitics calculates the maximum market cap for stocks from each sectors using the `AVERAGEIF` function. It shows that technology sector has the highest average market cap ($59,541,883,507.27), about two times of telecommunications at the second place ($28,555,181,149.03), and about three times of the customer discretionary ($18,506,403,179.63).

### 2.2 Chart
<img class="center" src="./images/analysis_chart.png"></img>
This pie chart shows the percentage of number stocks from each sector in the entire munged [dataset](./data/clean_data.csv). It shows that at about 80% of stocks in the dataset come evenly from "Consumer Discretionary," "Finance," "Healthcare," and "Technology" sectors. 

## 3. Extra-credit

This assignment deserves extra credit for **Big or Complex Data** because 
it munged a [dataset](./data/nasdaq_screener_20240206.csv) of **1590** records and analyzed a [dataset](./data/clean_data.csv) of **1569** records.