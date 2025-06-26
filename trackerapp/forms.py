from django import forms
from .models import Expense, Category

class ExpenseForm(forms.ModelForm):
    new_category = forms.CharField(
        required=False,
        label='New Category',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate dropdown with distinct categories
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].required = False  # Important: Allow blank when new_category is used

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')

        if not category and not new_category:
            raise forms.ValidationError("Please select or add a category.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        new_cat = self.cleaned_data.get('new_category')
        if new_cat:
            category_obj, _ = Category.objects.get_or_create(name=new_cat)
            instance.category = category_obj

        if commit:
            instance.save()
        return instance
