from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Resets PostgreSQL primary key sequences to match the current max ID.'

    def handle(self, *args, **options):
        # format: (table_name, primary_key_column)
        tables_to_fix = [
            ('users', 'u_userid'),
            ('vendors', 'v_vendorid'),
            ('user_transactions', 't_transid'),
            ('rewards', 'r_rewardid'),
            ('ledger', 'l_ledgerid'),
        ]

        with connection.cursor() as cursor:
            for table, pk in tables_to_fix:
                self.stdout.write(f"Fixing sequence for {table}...")
                
                # The SQL query to reset the sequence
                sql = f"""
                SELECT setval(
                    pg_get_serial_sequence('{table}', '{pk}'), 
                    COALESCE((SELECT MAX({pk}) FROM {table}), 1)
                );
                """
                try:
                    cursor.execute(sql)
                    result = cursor.fetchone()[0]
                    self.stdout.write(self.style.SUCCESS(f"  -> Set next value to {result + 1}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  -> Failed: {e}"))

        self.stdout.write(self.style.SUCCESS('All sequences synced successfully!'))