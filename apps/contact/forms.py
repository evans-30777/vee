from django import forms

from .models import ContactSubmission


class ContactForm(forms.ModelForm):
    # Bots fill hidden fields; humans leave this empty.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactSubmission
        fields = ["name", "email", "phone", "service", "budget", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].required = False
        self.fields["budget"].required = False
        self.fields["phone"].required = False

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Submission rejected.")
        return ""


class NewsletterForm(forms.Form):
    email = forms.EmailField()
    source = forms.CharField(required=False, max_length=80, widget=forms.HiddenInput)
