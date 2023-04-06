from django.db import models

from django.utils import timezone

    ################################################################
    # Model for ModelExchange Objects, representing Trading Venues #
    ################################################################

class ModelExchange(models.Model):
    value           = models.CharField(max_length=100, db_index=True)
    is_valid        = models.BooleanField(default=True)
    created_at      = models.DateTimeField(default=timezone.now)
    updated_at      = models.DateTimeField(default=timezone.now)
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=["value"],
                                               name='unique_exchange_value')]

    def __repr__(self):
        return f"<Exchange {self.value} - key: {self.id}>"
