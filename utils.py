def check_integer_format(text: str):
    if text == '':
        return True

    if all(x in '0123456789' for x in text):
        try:
            int(text)
            return True
        except ValueError:
            return False

    else:
        return False

def check_float_format(text: str):
    if text == '':
        return True

    if all(x in '0123456789.' for x in text) and text.count('.') <= 1:
        try:
            float(text)
            return True
        except ValueError:
            return False

    else:
        return False