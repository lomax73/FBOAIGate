from django import forms

from .models import Cliente, Postazione


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'note']
        widgets = {'note': forms.Textarea(attrs={'rows': 3})}


class PostazioneForm(forms.ModelForm):
    class Meta:
        model = Postazione
        fields = ['cliente', 'nome', 'rustdesk_id', 'sistema', 'note']
        widgets = {'note': forms.Textarea(attrs={'rows': 3})}
