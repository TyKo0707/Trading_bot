def check_integer_format(text: str) -> bool:

    """
    Check that the text is a positive integer
    :param text: Text entered by the user in a tk.Entry widget
    :return:
    """

    if text == "":
        return True

    if all(x in "0123456789" for x in text):
        try:
            int(text)
            return True
        except ValueError:
            return False

    else:
        return False


def check_float_format(text: str) -> bool:

    """
    Check that the text is a positive floating number
    :param text: Text entered by the user in a tk.Entry widget
    :return:
    """

    if text == "":
        return True

    if all(x in "0123456789." for x in text) and text.count(".") <= 1:
        try:
            float(text)
            return True
        except ValueError:
            return False

    else:
        return False
