import math

def calc_depreciation(printer_cost, lifespan_hrs, print_time_hrs):
    """Calculate machine depreciation cost for a print job."""
    if lifespan_hrs <= 0:
        return 0.0
    return (printer_cost / lifespan_hrs) * print_time_hrs

def calc_labour(setup_time_hrs, post_time_hrs, hourly_rate):
    """Calculate labour cost for setup and post-processing."""
    total_time = setup_time_hrs + post_time_hrs
    return total_time * hourly_rate

def apply_fail_rate(base_cost, fail_rate_pct):
    """Adjust cost for expected print failure rate (as percent, e.g. 10 for 10%)."""
    if fail_rate_pct >= 100:
        return math.inf  # Infinite cost if 100% fail
    return base_cost / (1 - fail_rate_pct / 100)

def calc_final_business_price(base_cost, fail_rate_pct, shipping_cost, markup_pct):
    """Calculate final business price including fail rate, shipping, and markup."""
    adjusted_cost = apply_fail_rate(base_cost, fail_rate_pct) + shipping_cost
    return adjusted_cost * (1 + markup_pct / 100) 