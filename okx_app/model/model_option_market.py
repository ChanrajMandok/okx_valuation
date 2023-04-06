from django.db import models

from okx_app.model.model_currency import ModelCurrency
from okx_app.model.model_exchange import ModelExchange

from django.utils import timezone

    #########################################################################
    # Model for ModelOptionMarket Objects, representing Options [Not in DB] #
    #########################################################################


class ModelOptionMarket(models.Model):
    exchange            = models.ForeignKey(ModelExchange, on_delete=models.CASCADE, null=False)
    base_currency       = models.ForeignKey(ModelCurrency, on_delete=models.CASCADE, null=False, related_name='option_base_currency')
    quote_currency      = models.ForeignKey(ModelCurrency, on_delete=models.CASCADE, null=False, related_name='option_quote_currency')
    option_type         = models.CharField(max_length=50)
    strike              = models.FloatField(null=False)
    bsm_implied_vol     = models.FloatField(null=True)
    vv_implied_vol_okby = models.FloatField(null=True)
    bid_price           = models.FloatField(null=True)
    bid_size            = models.FloatField(null=False)
    ask_price           = models.FloatField(null=True)
    ask_size            = models.FloatField(null=False)
    reference           = models.FloatField(null=False)
    term                = models.FloatField(null=False)
    source_id           = models.CharField(max_length=500, null=True)
    created_at          = models.DateTimeField(default=timezone.now)
    
    class Meta:
        managed=False
    
    def __str__(self):
        return '{}, {}, {}, {}, {}'.format(
                                    f'{self.base_currency.value}-{self.quote_currency.value}',
                                    self.option_type,
                                    self.strike,
                                    self.exchange.value,
                                    self.source_id)