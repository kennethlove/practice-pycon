from __future__ import absolute_import

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from . import models


class TalkListForm(forms.ModelForm):
    class Meta:
        fields = ('name',)
        model = models.TalkList

    def __init__(self, *args, **kwargs):
        super(TalkListForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            ButtonHolder(
                Submit('create', 'Create', css_class='btn-primary')
            )
        )


class TalkForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'when', 'room')
        model = models.Talk

    def __init__(self, *args, **kwargs):
        super(TalkForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'when',
            'room',
            ButtonHolder(
                Submit('add', 'Add', css_class='btn-primary')
            )
        )
