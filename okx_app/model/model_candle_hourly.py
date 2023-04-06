from django.db import models

from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange

    ###########################################################################
    # Model for ModelCandleHourly Objects, this Stores Binance 1 hour Candles #
    ###########################################################################


class ModelCandleHourly(models.Model):
    exchange        = models.ForeignKey(ModelExchange, on_delete=models.CASCADE, null=False)
    base_ccy        = models.ForeignKey(ModelCurrency, on_delete=models.CASCADE, null=False, related_name='%(class)sbase_ccy')
    quote_ccy       = models.ForeignKey(ModelCurrency, on_delete=models.CASCADE, null=False, related_name='%(class)squote_ccy')
    date            = models.DateTimeField(null=False)
    open            = models.FloatField(null=False)
    close           = models.FloatField(null=False)
    high            = models.FloatField(null=False)
    low             = models.FloatField(null=False)
    time_of_year    = models.CharField(max_length=20, null=True)
    
    class Meta:
        constraints = [
                models.UniqueConstraint(fields=["exchange", 
                                                "base_ccy", 
                                                "quote_ccy", 
                                                "time_of_year"],
                                                name='%(class)sunique_candle')
                        ]
    
    def __repr__(self):
        return f"<{self.base_ccy.value}/{self.quote_ccy.value};{self.date};{self.close}>"