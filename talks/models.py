from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

import mistune


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
    host = models.CharField(max_length=255)
    talk_rating = models.IntegerField(blank=True, default=0)
    speaker_rating = models.IntegerField(blank=True, default=0)
    notes = models.TextField(blank=True, default='')
    notes_html = models.TextField(blank=True, default='', editable=False)

    class Meta:
        ordering = ('when', 'room')
        unique_together = ('talk_list', 'name')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.notes_html = mistune.markdown(self.notes)
        super(Talk, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('talks:talks:detail', kwargs={'slug': self.slug})

    @property
    def overall_rating(self):
        if self.talk_rating and self.speaker_rating:
            return (self.talk_rating + self.speaker_rating) / 2
        return 0
