from django import forms


class GetNews(forms.Form):
    search_term = forms.CharField(max_length=250, required=False,  widget=forms.TextInput(attrs={
        'style': 'display:inline-block;width:100%'}))
    country = forms.CharField(label="Select Country For News", required=False,
                              widget=forms.TextInput(
                                  attrs={'list': 'countries',
                                         'autocomplete': 'off',
                                         'style': 'display:inline-block'}))
    category = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'list': 'category',
               'autocomplete': 'off',
               'style': 'display:inline-block'}))
