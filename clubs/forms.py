from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator

from .models import User, Club


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible"""

        user = None
        if self.is_valid():
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
        return user


class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """ Ensure that new_password and password_confirmation contain the same password."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""

        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(email=self.user.email, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'experience_level', 'personal_statement']
        widgets = {
            'bio': forms.Textarea(),
            'experience_level': forms.Textarea(),
            'personal_statement': forms.Textarea()
        }

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message="Password must contain an uppercase character, a lowercase character and a number."
        )]
    )
    password_confirmation = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())

    def save(self):
        """Create a new user."""
        super().save(commit=False)
        user = User.objects.create_user(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            bio=self.cleaned_data.get('bio'),
            experience_level=self.cleaned_data.get('experience_level'),
            personal_statement=self.cleaned_data.get('personal_statement'),
            password=self.cleaned_data.get('new_password')
        )
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'experience_level', 'personal_statement']
        widgets = {'bio': forms.Textarea()}


class CreateClubForm(forms.ModelForm):
    """Form to create a club."""

    class Meta:
        """Form options."""

        model = Club
        fields = ['name', 'location', 'mission_statement']
        widgets = {'mission_statement': forms.Textarea()}
