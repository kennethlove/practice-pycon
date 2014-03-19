from __future__ import absolute_import

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from .models import TalkList


class TalkListForm(forms.ModelForm):
    class Meta:
        fields = ('name',)
        model = TalkList

    def __init__(self, *args, **kwargs):
        super(TalkListForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            ButtonHolder(
                Submit('create', 'Create', css_class='btn-primary')
            )
        )
