SUPPORTED_CURRENCIES = {'INR', 'USD', 'AED', 'EUR', 'GBP'}

def is_supported_currency(code):
    return isinstance(code, str) and code.strip().upper() in SUPPORTED_CURRENCIES
