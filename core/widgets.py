from wtforms.widgets import Input
from markupsafe import Markup # Correct import for HTMLString


class BootstrapSwitchInput(Input):
    """
    Renders an HTML input type="checkbox" with Bootstrap's form-check-input and role="switch" classes.
    This widget expects the surrounding div.form-check.form-switch and label to be rendered separately
    in the Jinja2 template for full Bootstrap switch functionality.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('type', 'checkbox')
        # Add the Bootstrap classes for the input itself
        kwargs['class'] = (kwargs.get('class', '') + ' form-check-input').strip()
        kwargs['role'] = 'switch'

        # Ensure 'checked' attribute is added if field.data is True
        if field.data:
            kwargs['checked'] = True

        # Render only the input tag using Markup
        return Markup(f'<input {self.html_params(name=field.name, id=field.id, **kwargs)}>')