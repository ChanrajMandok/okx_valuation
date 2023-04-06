from okx_app.services.volatility_historical.service_volatility_historical_standard_deviation_estimator import ServiceVolatilityHistoricalStandardDeviationEstimator
from okx_app.services.volatility_historical.service_volatility_historical_garch_forecast_estimator import ServiceVolatilityHistoricalGarchForecastEstimator
from okx_app.services.volatility_historical.service_volatility_historical_kalman_filter_estimator import ServiceVolatilityHistoricalKalmanFilterEstimator
from okx_app.services.volatility_historical.service_volatility_historical_sub_sampled_estimator import ServiceVolatilityHistoricalSubSampledEstimator
from okx_app.services.volatility_historical.service_volatility_historical_vvol_estimator import ServiceVolatilityHistoricalVvolEstimator
from okx_app.services.volatility_historical.service_volatility_historical_yang_zhang_estimator import ServiceVolatilityHistoricalYangZhangEstimator

service_volatility_historical_estimator                  = ServiceVolatilityHistoricalStandardDeviationEstimator()
service_volatility_historical_garch_estimator            = ServiceVolatilityHistoricalGarchForecastEstimator()
service_volatility_historical_kalman_filter_estimator    = ServiceVolatilityHistoricalKalmanFilterEstimator()
service_volatility_historical_sub_sampled_estimator      = ServiceVolatilityHistoricalSubSampledEstimator()
service_volatility_historical_vvol_estimator             = ServiceVolatilityHistoricalVvolEstimator()
service_volatility_historical_yang_zhang_estimator       = ServiceVolatilityHistoricalYangZhangEstimator()

    #################################################################
    # Decorator imports all historical Vol Estimators for interface #
    #################################################################


def decorator_historical_estimator_interface_imports(func):
    """
    Decorator for all historical Vol Estimators to a function.
    """
    def wrapper(*args, **kwargs):
        return func(*args, 
                     service_volatility_historical_estimator               = service_volatility_historical_estimator,
                     service_volatility_historical_garch_estimator         = service_volatility_historical_garch_estimator,
                     service_volatility_historical_kalman_filter_estimator = service_volatility_historical_kalman_filter_estimator,
                     service_volatility_historical_sub_sampled_estimator   = service_volatility_historical_sub_sampled_estimator,
                     service_volatility_historical_vvol_estimator          = service_volatility_historical_vvol_estimator,
                     service_volatility_historical_yang_zhang_estimator    = service_volatility_historical_yang_zhang_estimator,
                     **kwargs)

    return wrapper

