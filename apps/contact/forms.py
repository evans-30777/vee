from django import forms

from .models import ContactSubmission


class ContactForm(forms.ModelForm):
    # Bots fill hidden fields; humans leave this empty.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactSubmission
        fields = ["name", "email", "phone", "service", "budget", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name", "autocomplete": "name"}),
            "email": forms.EmailInput(
                attrs={"placeholder": "you@business.co.ke", "autocomplete": "email"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "07xx xxx xxx", "autocomplete": "tel", "inputmode": "tel"}
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": (
                        "What does your business do, and what would you like to improve online?"
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].required = False
        self.fields["budget"].required = False
        self.fields["phone"].required = False

        self.fields["service"].label = "What are you interested in?"
        self.fields["budget"].label = "Monthly budget"
        self.fields["phone"].label = "Phone or WhatsApp number"
        self.fields["message"].label = "How can we help?"

        # These render as plain choice fields, so the blank option is replaced
        # on the choices themselves rather than via empty_label.
        self.fields["service"].choices = [
            ("", "Not sure yet"), *ContactSubmission.Service.choices
        ]
        self.fields["budget"].choices = [
            ("", "Not sure yet"), *ContactSubmission.Budget.choices
        ]

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Submission rejected.")
        return ""


class NewsletterForm(forms.Form):
    email = forms.EmailField()
    source = forms.CharField(required=False, max_length=80, widget=forms.HiddenInput)
