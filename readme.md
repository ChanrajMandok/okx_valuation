
# **OKX Pricing**

# Setup OKX_Pricing

|Action|Command
| :-| :-
|Create a virtual environment| python -m venv .venv
|Install relevant libraries | pip install -r requirements.txt|
|Create a .env file and add it to the root | .env
|Create DB on local machine | PGadmin -> servers -> postgres -> databases -> create -> okx|
|User needs Binance credentials to run historical Vol (plot still works without this)| https://accounts.binance.com/en/register|
|Create json launch file| Open and Paste contents of launch_items.txt (ensure commas are correct)|
|register models in  okx_app\models.py | Models in list_of models.txt|
|Run Make Migrations|Run & debug -> dropdown Menu -> Make Migrations |
|If  No Migration Changes |Ensure migrations folder with blank __init__.py file in |
|Run Migrations|Run & debug -> dropdown menu -> Migrate |
|Run Populate Tables| Run & debug -> dropdown menu -> populate tables |
|Run Volatility Plot | Run & debug -> dropdown menu -> Run Volatility Plot |


# Enviroment Variables

|Environment variable|value|
| :-| :-
|BINANCE_API_KEY|
|BINANCE_SECRET_KEY|
|DATABASE_NAME|okx|
|DATABASE_USER|postgres|
|DATABASE_PASSWORD||
|DATABASE_PORT||
|TIME_TO_MATURITY_MIN_DAYS|0.1|
|TIME_TO_MATURITY_MAX_DAYS|50|


# Disclaimer

This trading research repository was created as a proof of theory/concept and should not be utilized in a trading environment. The code in this repository is provided for educational purposes only, and it is the sole responsibility of the user to determine whether the code is suitable for their intended use. The author of this repository does not make any representation or warranty as to the accuracy, completeness, or reliability of the information contained herein. The user should be aware that there are risks associated with trading and that trading decisions should only be made after careful consideration of all relevant factors. The author of this repository will not be held responsible for any losses that may result from the use of this code.


# Executive Summary

This repository retrieves all ETH–USD Options from OKX with a maturity of less than TIME_TO_MATURITY_MAX_DAYS days and creates ModelOptionMarket objects that hold all the required information such as the strike price, option type, spot price, ask price, ask size, bid size, bid price, maturity, base currency, and quote currency. The Black-Scholes-Merton (BSM) option pricing model is then used to price these options. The BSM model is a mathematical model used to price options by considering factors such as the spot price, strike price, time to expiration, volatility, and interest rates. This model was developed by Fischer Black, Myron Scholes, and Robert Merton in 1973 and is widely used in the finance industry to value options. However, it has some limitations, such as assuming that the underlying asset price follows a lognormal distribution, which does not hold in periods of Financial turmoil.

The options are then divided into different maturities, and for each maturity, the implied volatility is plotted to produce the volatility surface area. The volatility surface area gives a visual representation of the implied volatility across different strikes and maturities. The volatility surface area helps traders to understand the market's perception of future volatility and identify potiential asymmetries in option pricing. Additionally, the volatility smile is plotted for each maturity. The volatility smile shows the relationship between implied volatility and strike price for a single maturity. The term "smile" arises from the shape of the curve, which resembles a smile. The volatility smile was first observed after the 1987 stock market crash and has become a foundation in the field of quantitative finance. The smile demonstrates that the implied volatility is not constant but varies with the strike price of the option. 

These volatility smiles are plotted to display the IV smile/curve which would be utilised by the ServiceOptionMarketImpliedVolVannaVolgaEstimator to derive the implied volatilty smile from 3 available quotes for a given maturity. This empirically verified method provides a robust valuation framework for exotic/non-standard derivatives.

Finally, if the code is provided with Binance keys, it will calculate the historical volatility measures from the historical volatility file in services (<3 DTE options only). This includes empirically verified methods such as Rodgers-Sachall, Yhang Zhang, Subsampled volatility, Volatility of Volatility, Garch(1,1) volatility Forecast and finally a Kalman Filter applied upon the volatility dataset. These measures can provide additional infomation when pricing Options. 

## Option Valuation Model
Implied volatility estimations are done using the Newton-Raphson method to approximate the Implied Volatility in the Black-Scholes-Merton model. The Newton-Raphson method offers an efficient approach to approximate the implied volatility, via iteratively refining an initial guess for the implied volatility until the calculated option price converges to the market price within a desired precision. The Newton-Raphson method is ideal for this application due to its rapid convergence when compared to alternative models such as brute-force searching or bisection methods may require a larger number of calculations, resulting in higher latency.


# Plot Ouputs


![VSA](ouput_images/volatilty_surface_area.png)


![50DTE](ouput_images/50dte_smile.png)
![22DTE](ouput_images/22dte_smile.png)
![15DTE](ouput_images/15dte_smile.png)
![8DTE](ouput_images/8dte_smile.png)
![2DTE](ouput_images/2dte_smile.png)