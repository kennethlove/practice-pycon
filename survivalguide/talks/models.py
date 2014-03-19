from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify


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
