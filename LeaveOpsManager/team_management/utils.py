from datetime import date, timedelta


def generate_assignments(employee, start_date, end_date):
    current_date = start_date
    pattern = employee.shift_pattern
    blocks = list(pattern.blocks.all())
    total_days = sum(block.days_on + block.days_off for block in blocks)

    while current_date <= end_date:
        day_in_cycle = (current_date - pattern.start_date).days % total_days
        cumulative_days = 0

        for block in blocks:
            if cumulative_days <= day_in_cycle < cumulative_days + block.days_on:
                if (day_in_cycle - cumulative_days) % 7 in block.working_days:
                    ShiftAssignment.objects.create(
                        employee=employee,
                        shift_block=block,
                        date=current_date
                    )
                break
            cumulative_days += block.days_on + block.days_off

        current_date += timedelta(days=1)


# Usage
start_date = date(2024, 7, 1)
end_date = date(2024, 8, 31)
generate_assignments(employee, start_date, end_date)