from okx_app.services.plot.service_plot_volatilty_surface_area import ServicePlotVolatilitySurfaceArea
from okx_app.services.plot.service_plot_volatilty_smile import ServicePlotVolatilitySmile

service_plot_volatilty_surface_area    = ServicePlotVolatilitySurfaceArea
service_plot_volatilty_smile           = ServicePlotVolatilitySmile

    ################################################################
    # Decorator imports all Plot Volatility Services for interface #
    ################################################################


def decorator_plot_volatilty_interface_imports(func):
    """
    Decorator for importing all Market Retrievers to a function.
    """
    def wrapper(*args, **kwargs):
        return func(*args, 
                     service_plot_volatilty_surface_area   = service_plot_volatilty_surface_area,
                     service_plot_volatilty_smile          = service_plot_volatilty_smile,
                     **kwargs)

    return wrapper