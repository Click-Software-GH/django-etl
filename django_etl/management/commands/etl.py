"""
Django ETL Framework Management Command
Provides command-line interface for ETL operations
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django_etl.utils import ETLUtils
import json
import sys


class Command(BaseCommand):
    help = "Analyze, validate, and preview ETL operations"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["analyze", "duplicates", "preview", "estimate"],
            help="ETL action to perform",
        )
        parser.add_argument("--table", required=True, help="Table name to analyze")
        parser.add_argument(
            "--database", default="default", help="Database alias to use"
        )
        parser.add_argument("--columns", help="Comma-separated list of columns")
        parser.add_argument("--limit", type=int, default=10, help="Limit for preview")
        parser.add_argument(
            "--batch-size", type=int, default=1000, help="Batch size for estimation"
        )
        parser.add_argument("--output", help="Output file for results")

    def handle(self, *args, **options):
        action = options["action"]
        table = options["table"]
        database = options["database"]

        result = None

        try:
            if action == "analyze":
                result = ETLUtils.analyze_table_quality(table, database)

            elif action == "duplicates":
                if not options["columns"]:
                    raise CommandError("--columns required for duplicates command")
                columns = [col.strip() for col in options["columns"].split(",")]
                result = ETLUtils.find_duplicates_in_table(table, columns, database)

            elif action == "preview":
                if not options["columns"]:
                    raise CommandError("--columns required for preview command")
                columns = [col.strip() for col in options["columns"].split(",")]
                result = ETLUtils.preview_transformation(
                    table, columns, database, options["limit"]
                )

            elif action == "estimate":
                result = ETLUtils.estimate_transformation_time(
                    table, database, options["batch_size"]
                )

            # Output results
            if result:
                output_json = json.dumps(result, indent=2, default=str)

                if options["output"]:
                    with open(options["output"], "w") as f:
                        f.write(output_json)
                    self.stdout.write(
                        self.style.SUCCESS(f'Results saved to {options["output"]}')
                    )
                else:
                    self.stdout.write(output_json)

        except Exception as e:
            raise CommandError(f"ETL operation failed: {e}")
