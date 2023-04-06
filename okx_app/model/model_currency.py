from django.utils import timezone
from django.db import models

from okx_app.model.model_exchange import ModelExchange

    ###########################################################
    # Model for ModelCurrency Objects from any venue/exchange #
    ###########################################################

class ModelCurrency(models.Model):
    value         = models.CharField(max_length=10, db_index=True)
    description   = models.CharField(max_length=50)
    created_at    = models.DateTimeField(default=timezone.now)
    updated_at    = models.DateTimeField(default=timezone.now)
    exchange      = models.ForeignKey(ModelExchange, on_delete=models.CASCADE, null=False, default=False) 
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=["value"],
                                               name='unique_currency_value')]

    def __repr__(self):
        return f"<Currency {self.value} - key: {self.key}>"
    
    @staticmethod
    def get_currency_from_str(currency_str: str):
        currency_tpl = ModelCurrency.objects.get_or_create(
                        value = currency_str,
                        defaults={
                            "description": currency_str
                                    })
        
        currency = currency_tpl[0]
        return currency
