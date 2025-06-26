from decimal import Decimal
from collections import defaultdict
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render, get_object_or_404, redirect
from .models import Expense, Category
from .forms import ExpenseForm

# Home view (add expenses)
def home(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            new_cat = form.cleaned_data.get("new_category")
            if new_cat:
                category_obj, _ = Category.objects.get_or_create(name=new_cat)
                expense = form.save(commit=False)
                expense.category = category_obj
                expense.save()
            else:
                form.save()
            return redirect('home')
    else:
        form = ExpenseForm()

    # Show all expenses sorted by date descending
    expenses = Expense.objects.all().order_by('-date')
    total = sum(exp.amount for exp in expenses)

    # Group expenses by category
    expenses_by_category = defaultdict(list)
    for exp in expenses:
        expenses_by_category[str(exp.category)].append(exp)

    # Total amount per category
    category_totals = {
        cat: sum(exp.amount for exp in exps)
        for cat, exps in expenses_by_category.items()
    }

    return render(request, 'trackerapp/home.html', {
        'form': form,
        'expenses': expenses,
        'total': total,
        'expenses_by_category': dict(expenses_by_category),
        'category_totals': category_totals,
    })


# Trends view with optional "group_by" filtering
def trends(request):
    group_by = request.GET.get('group_by', 'daily')
    expenses = Expense.objects.all()

    category_totals = defaultdict(lambda: Decimal('0.0'))
    for exp in expenses:
        category_totals[exp.category] += exp.amount

    highest = max(category_totals.items(), key=lambda x: x[1], default=("N/A", Decimal(0)))
    lowest = min(category_totals.items(), key=lambda x: x[1], default=("N/A", Decimal(0)))

    # Pie chart
    fig1, ax1 = plt.subplots()
    ax1.pie(category_totals.values(), labels=[str(k) for k in category_totals.keys()], autopct='%1.1f%%')
    ax1.set_title("Expenses by Category")
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    category_chart = base64.b64encode(buf1.read()).decode('utf-8')
    buf1.close()
    plt.clf()

    # Trend line chart
    trend_totals = defaultdict(lambda: Decimal('0.0'))
    for exp in expenses:
        if group_by == 'monthly':
            key = exp.date.strftime('%Y-%m')
        elif group_by == 'yearly':
            key = exp.date.strftime('%Y')
        elif group_by == 'weekly':
            key = f"{exp.date.year}-W{exp.date.isocalendar()[1]}"
        else:  # daily
            key = exp.date.strftime('%Y-%m-%d')
        trend_totals[key] += exp.amount

    sorted_keys = sorted(trend_totals)
    totals = [trend_totals[k] for k in sorted_keys]

    fig2, ax2 = plt.subplots()
    ax2.plot(sorted_keys, totals, marker='o')
    ax2.set_title(f"Spending Over Time ({group_by.capitalize()})")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Amount ($)")
    plt.xticks(rotation=45)
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    time_chart = base64.b64encode(buf2.read()).decode('utf-8')
    buf2.close()
    plt.clf()

    return render(request, 'trackerapp/trends.html', {
        'category_chart': category_chart,
        'time_chart': time_chart,
        'highest_category': highest[0],
        'highest_amount': highest[1],
        'lowest_category': lowest[0],
        'lowest_amount': lowest[1],
        'group_by': group_by,
    })


# Edit view
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'trackerapp/edit_expense.html', {'form': form})


# Delete view
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    return redirect('home')
