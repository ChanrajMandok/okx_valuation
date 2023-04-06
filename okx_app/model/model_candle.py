from django.db import models

from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange

    ####################################################################
    # Model for ModelCandle Objects, this Stores Binance 1 min Candles #
    ####################################################################

class ModelCandle(models.Model):
    exchange        = models.ForeignKey(ModelExchange, on_delete=models.CASCADE, null=False)
    base_ccy        = models.ForeignKey(ModelCurrency, on_delete=models.CASCADE, null=False, related_name='base_ccy')
    quote_ccy       = models.ForeignKey(ModelCurrency, on_delete=models.CASCADE, null=False, related_name='quote_ccy')
    date            = models.DateTimeField(null=False)
    open            = models.FloatField(null=False)
    close           = models.FloatField(null=False)
    high            = models.FloatField(null=False)
    low             = models.FloatField(null=False)
    fill_method     = models.CharField(max_length=20, null=True)
    time_of_week    = models.CharField(max_length=20, null=True)
    
    class Meta:
        constraints = [
                models.UniqueConstraint(fields=["exchange",
                                                "base_ccy",
                                                "quote_ccy",
                                                "time_of_week"],
                                                name='unique_candle')
                        ]
    
    def __repr__(self):
        return f"<{self.base_ccy.value}/{self.quote_ccy.value};{self.date};{self.close}>"