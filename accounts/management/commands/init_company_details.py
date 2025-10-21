from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from accounts.models import CompanyContactDetails


class Command(BaseCommand):
    help = "Initialize or update company contact details"

    def add_arguments(self, parser):
        parser.add_argument(
            "--legal-name",
            type=str,
            help="Legal entity name",
        )
        parser.add_argument(
            "--trading-name",
            type=str,
            help="Trading name",
        )
        parser.add_argument(
            "--arn",
            type=str,
            help="Aviation Reference Number",
        )
        parser.add_argument(
            "--abn",
            type=str,
            help="Australian Business Number",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update existing details",
        )

    def handle(self, *args, **options):
        try:
            # Get or create the singleton instance
            company_details = CompanyContactDetails.get_instance()

            updated_fields = []

            # Update fields if provided
            if options["legal_name"]:
                company_details.legal_entity_name = options["legal_name"]
                updated_fields.append("legal_entity_name")

            if options["trading_name"]:
                company_details.trading_name = options["trading_name"]
                updated_fields.append("trading_name")

            if options["arn"]:
                company_details.arn = options["arn"]
                updated_fields.append("arn")

            if options["abn"]:
                company_details.abn = options["abn"]
                updated_fields.append("abn")

            if updated_fields or options["force"]:
                company_details.full_clean()  # Validate the model
                company_details.save()

                if updated_fields:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully updated company details: {', '.join(updated_fields)}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS("Company details initialized successfully")
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "No changes made. Use --force to initialize with defaults or provide field arguments."
                    )
                )

            # Display current details
            self.stdout.write("\nCurrent Company Details:")
            self.stdout.write(f"Legal Name: {company_details.legal_entity_name}")
            self.stdout.write(f"Trading Name: {company_details.trading_name}")
            self.stdout.write(f"ARN: {company_details.arn}")
            self.stdout.write(f"ABN: {company_details.abn}")
            self.stdout.write(f"Last Updated: {company_details.updated_at}")

        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f"Validation error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating company details: {e}"))
