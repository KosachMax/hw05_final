from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        help_text='Model unit pub date',
        auto_now_add=True
    )

    class Meta:
        abstract = True
