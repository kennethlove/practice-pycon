import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.timezone import utc


class TalkList(models.Model):
    user = models.ForeignKey(User, related_name='lists')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)

    class Meta:
        unique_together = ('user', 'name')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(TalkList, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('talks:lists:detail', kwargs={'slug': self.slug})


class Talk(models.Model):
    ROOM_CHOICES = (
        ('517D', '517D'),
        ('517C', '517C'),
        ('517AB', '517AB'),
        ('520', '520'),
        ('710A', '710A')
    )
    talk_list = models.ForeignKey(TalkList, related_name='talks')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    when = models.DateTimeField()
    room = models.CharField(max_length=10, choices=ROOM_CHOICES)

    class Meta:
        unique_together = ('talk_list', 'name')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Talk, self).save(*args, **kwargs)

    def clean(self):
        pycon_start = datetime.datetime(2014, 4, 11).replace(tzinfo=utc)
        pycon_end = datetime.datetime(2014, 4, 13, 17).replace(tzinfo=utc)
        if not pycon_start < self.when < pycon_end:
            raise ValidationError("'when' is outside of PyCon.")
