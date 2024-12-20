from django.db import models
from django.utils.translation import gettext_lazy as _


class Abstract(models.Model):
    
    modtime = models.DateTimeField(_("末次时间"), auto_now=True)
    addtime = models.DateTimeField(_("首次时间"), auto_now_add=True)
    
    class Meta:
        abstract = True
        ordering = ("-addtime",)
