from django.contrib.auth.forms import (PasswordChangeForm, PasswordResetForm,
                                       UserCreationForm, SetPasswordForm)
from django.contrib.auth import get_user_model

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        help_text = 'Форма регистрации'  # Added help_text for all forms


class PassChangeForm(PasswordChangeForm):
    class Meta(PasswordChangeForm):
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')
        help_text = 'Изменения пароля'


class PassResetForm(PasswordResetForm):
    class Meta(PasswordResetForm):
        model = User
        fields = 'email'
        help_text = 'Сброс пароля по email'


class PassSetForm(SetPasswordForm):
    class Meta(SetPasswordForm):
        model = User
        fields = ('new_password1', 'new_password2')
        help_text = 'Создание нового пароля'
