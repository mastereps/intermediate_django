from django import forms

from .models import Profile


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image"]
        widgets = {
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "block w-full text-sm text-slate-600 file:mr-4 file:rounded-xl file:border-0 file:bg-indigo-700 file:px-4 file:py-2 file:font-semibold file:text-white hover:file:bg-slate-900",
                    "accept": "image/*",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False

