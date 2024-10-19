from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import password_validation


# Local imports
from .models import Operator, Personal


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields.pop('password2')

    class Meta:
        model = Operator
        fields = ('name', 'family', 'NID', 'PID', 'phone', 'department', 'job', 'expire', 'username', 'password1', )


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(),
    )


class PersonalRegistrationForm(forms.ModelForm):
    class Meta:
        model = Personal
        fields = '__all__'


class PasswordChangeForm(forms.Form):
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )

    NID = forms.CharField(max_length=10, label='NID')
    PID = forms.CharField(max_length=20, label='PID')

    class Meta:
        fields = ('PID', 'NID', 'password1', 'password2')

    def clean_password2(self):
        print(self.cleaned_data)
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            print("clean pass err")
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def clean(self):
        print(self.cleaned_data)
        cleaned_data = super().clean()
        pid = cleaned_data.get('PID')
        nid = cleaned_data.get('NID')
        self.user_obj = Operator.objects.filter(PID=pid, NID=nid).first()
        if not self.user_obj:
            print("clean pass err")
            raise forms.ValidationError('Invalid PID or NID')
        
    def save(self, commit=True):
        print(self.cleaned_data)
        user = self.user_obj
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
        
