from django.core.management.base import BaseCommand
from trackerapp.models import Category, Expense
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = "Seed the database with sample categories and expenses"

    def handle(self, *args, **kwargs):
        # Clear existing data (optional)
        Expense.objects.all().delete()
        Category.objects.all().delete()

        # Sample categories
        categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Health', 'Shopping']
        category_objs = []

        for name in categories:
            cat = Category.objects.create(name=name)
            category_objs.append(cat)

        # Create sample expenses
        today = date.today()
        for i in range(30):  # last 30 days
            exp_date = today - timedelta(days=i)
            for _ in range(random.randint(1, 3)):  # 1–3 expenses per day
                category = random.choice(category_objs)
                amount = round(random.uniform(5, 100), 2)
                Expense.objects.create(
                    category=category,
                    amount=amount,
                    date=exp_date
                )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with test data!"))
