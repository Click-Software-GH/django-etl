#!/usr/bin/env python3
"""
ETL Utility Script
Provides common ETL operations and data analysis tools
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")
django.setup()

from django.db import connections
from .helpers import DataCleaner, HashGenerator
import argparse
import json


class ETLUtils:
    """Collection of ETL utility functions"""

    @staticmethod
    def analyze_table_quality(table_name, database="legacy"):
        """
        Analyze data quality of a table

        Args:
            table_name: Name of the table to analyze
            database: Database alias to use

        Returns:
            Dictionary with quality metrics
        """
        with connections[database].cursor() as cursor:
            # Get basic stats
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]

            # Get column info (database-agnostic)
            columns = ETLUtils._get_table_columns(cursor, table_name, database)

            quality_report = {
                "table_name": table_name,
                "total_rows": total_rows,
                "columns": columns,
                "quality_issues": {},
            }

            # Check for null values in each column
            for column in columns:
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE {column} IS NULL"
                )
                null_count = cursor.fetchone()[0]

                if null_count > 0:
                    quality_report["quality_issues"][f"{column}_nulls"] = {
                        "count": null_count,
                        "percentage": round((null_count / total_rows) * 100, 2),
                    }

            # Check for empty strings in text columns
            for column in columns:
                try:
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {table_name} WHERE {column} = ''"
                    )
                    empty_count = cursor.fetchone()[0]

                    if empty_count > 0:
                        quality_report["quality_issues"][f"{column}_empty"] = {
                            "count": empty_count,
                            "percentage": round((empty_count / total_rows) * 100, 2),
                        }
                except:
                    # Column might not be text type
                    pass

            return quality_report

    @staticmethod
    def find_duplicates_in_table(table_name, columns, database="legacy"):
        """
        Find duplicate records in a table based on specific columns

        Args:
            table_name: Name of the table
            columns: List of column names to check for duplicates
            database: Database alias

        Returns:
            List of duplicate groups
        """
        with connections[database].cursor() as cursor:
            column_list = ", ".join(columns)

            sql = f"""
            SELECT {column_list}, COUNT(*) as count
            FROM {table_name}
            GROUP BY {column_list}
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            """

            cursor.execute(sql)
            duplicates = cursor.fetchall()

            return [
                {"values": dict(zip(columns, row[:-1])), "count": row[-1]}
                for row in duplicates
            ]

    @staticmethod
    def preview_transformation(table_name, columns, database="legacy", limit=10):
        """
        Preview how data will look after transformation

        Args:
            table_name: Source table name
            columns: List of columns to preview
            database: Database alias
            limit: Number of rows to preview

        Returns:
            List of original and transformed data
        """
        with connections[database].cursor() as cursor:
            column_list = ", ".join(columns)
            cursor.execute(f"SELECT {column_list} FROM {table_name} LIMIT {limit}")

            rows = cursor.fetchall()
            preview = []

            for row in rows:
                original = dict(zip(columns, row))
                transformed = {}

                for i, value in enumerate(row):
                    column = columns[i]

                    # Apply common transformations
                    cleaned = DataCleaner.clean_string(value)
                    transformed[column] = {
                        "original": value,
                        "cleaned": cleaned,
                        "title_case": cleaned.title() if cleaned else "",
                        "length": len(str(value)) if value else 0,
                    }

                preview.append({"original": original, "transformed": transformed})

            return preview

    @staticmethod
    def estimate_transformation_time(table_name, database="legacy", batch_size=1000):
        """
        Estimate how long a transformation will take

        Args:
            table_name: Source table name
            database: Database alias
            batch_size: Batch size for processing

        Returns:
            Time estimates
        """
        import time

        with connections[database].cursor() as cursor:
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]

            # Time a small batch
            start_time = time.time()
            cursor.execute(
                f"SELECT * FROM {table_name} LIMIT {min(batch_size, total_rows)}"
            )
            sample_rows = cursor.fetchall()

            # Simulate processing
            for row in sample_rows:
                for value in row:
                    DataCleaner.clean_string(value)

            processing_time = time.time() - start_time

            # Calculate estimates
            rows_per_second = (
                len(sample_rows) / processing_time if processing_time > 0 else 1000
            )
            estimated_total_time = total_rows / rows_per_second
            estimated_batches = (total_rows + batch_size - 1) // batch_size

            return {
                "total_rows": total_rows,
                "sample_size": len(sample_rows),
                "processing_time_sample": round(processing_time, 2),
                "rows_per_second": round(rows_per_second, 2),
                "estimated_total_time_seconds": round(estimated_total_time, 2),
                "estimated_total_time_minutes": round(estimated_total_time / 60, 2),
                "estimated_batches": estimated_batches,
            }

    @staticmethod
    def _get_table_columns(cursor, table_name, database="legacy"):
        """
        Get column names from a table in a database-agnostic way

        Args:
            cursor: Database cursor
            table_name: Name of the table
            database: Database alias

        Returns:
            List of column names
        """
        connection = connections[database]
        vendor = connection.vendor

        if vendor == "mysql":
            cursor.execute(f"DESCRIBE {table_name}")
            # MySQL DESCRIBE returns: Field, Type, Null, Key, Default, Extra
            columns = [row[0] for row in cursor.fetchall()]
        elif vendor == "sqlite":
            cursor.execute(f"PRAGMA table_info({table_name})")
            # SQLite PRAGMA returns: cid, name, type, notnull, dflt_value, pk
            columns = [row[1] for row in cursor.fetchall()]
        elif vendor == "postgresql":
            cursor.execute(
                f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """
            )
            columns = [row[0] for row in cursor.fetchall()]
        else:
            # Fallback: try to get columns from a simple query
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
                columns = [desc[0] for desc in cursor.description]
            except Exception as e:
                raise Exception(
                    f"Unsupported database vendor '{vendor}' and fallback failed: {e}"
                )

        return columns


def main():
    parser = argparse.ArgumentParser(description="ETL Utility Commands")
    parser.add_argument(
        "command", choices=["analyze", "duplicates", "preview", "estimate"]
    )
    parser.add_argument("--table", required=True, help="Table name to analyze")
    parser.add_argument("--columns", help="Comma-separated list of columns")
    parser.add_argument("--database", default="legacy", help="Database alias")
    parser.add_argument("--limit", type=int, default=10, help="Limit for preview")
    parser.add_argument(
        "--batch-size", type=int, default=1000, help="Batch size for estimation"
    )
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    result = None

    if args.command == "analyze":
        result = ETLUtils.analyze_table_quality(args.table, args.database)

    elif args.command == "duplicates":
        if not args.columns:
            print("Error: --columns required for duplicates command")
            sys.exit(1)
        columns = [col.strip() for col in args.columns.split(",")]
        result = ETLUtils.find_duplicates_in_table(args.table, columns, args.database)

    elif args.command == "preview":
        if not args.columns:
            print("Error: --columns required for preview command")
            sys.exit(1)
        columns = [col.strip() for col in args.columns.split(",")]
        result = ETLUtils.preview_transformation(
            args.table, columns, args.database, args.limit
        )

    elif args.command == "estimate":
        result = ETLUtils.estimate_transformation_time(
            args.table, args.database, args.batch_size
        )

    # Output results
    if result:
        output_json = json.dumps(result, indent=2, default=str)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output_json)
            print(f"Results saved to {args.output}")
        else:
            print(output_json)


if __name__ == "__main__":
    main()
