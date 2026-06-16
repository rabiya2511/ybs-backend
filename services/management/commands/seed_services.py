from django.core.management.base import BaseCommand
from services.models import Service

class Command(BaseCommand):
    help = 'Seed all 12 YBS services into the database'

    def handle(self, *args, **kwargs):
        services_data = [
            {"name": "Brand Identity", "category": "Design", "icon": "x", "starting_price": 8999, "description": "Logo, color palette, typography and brand guidelines"},
            {"name": "Website Design", "category": "Tech", "icon": "x", "starting_price": 24999, "description": "Corporate sites, landing pages and e-commerce"},
            {"name": "Mobile App Dev", "category": "Tech", "icon": "x", "starting_price": 79999, "description": "iOS and Android native and cross-platform apps"},
            {"name": "Accounting & GST", "category": "Finance", "icon": "x", "starting_price": 2999, "description": "Bookkeeping, GST filing, TDS returns"},
            {"name": "Digital Marketing", "category": "Design", "icon": "x", "starting_price": 14999, "description": "SEO, Google Ads, social media management"},
            {"name": "Legal Compliance", "category": "Legal", "icon": "x", "starting_price": 5999, "description": "MCA, ROC annual filings and secretarial services"},
            {"name": "IP & Trademarks", "category": "Legal", "icon": "x", "starting_price": 6999, "description": "Brand protection, trademark filing and monitoring"},
            {"name": "HR & Payroll", "category": "Finance", "icon": "x", "starting_price": 3499, "description": "PF, ESI, salary management and employee onboarding"},
            {"name": "FSSAI License", "category": "Food & ISO", "icon": "x", "starting_price": 2499, "description": "Food business registration - Basic, State and Central"},
            {"name": "ISO Certification", "category": "Food & ISO", "icon": "x", "starting_price": 18999, "description": "ISO 9001, 14001, 27001 certification and consulting"},
            {"name": "Startup Funding", "category": "Finance", "icon": "x", "starting_price": 9999, "description": "Pitch deck, financial modeling and investor connect"},
        ]

        for s in services_data:
            obj, created = Service.objects.get_or_create(
                name=s["name"],
                defaults=s
            )
            if created:
                self.stdout.write(f"Added: {s['name']}")
            else:
                self.stdout.write(f"Already exists: {s['name']}")

        self.stdout.write("Done! All services seeded.")