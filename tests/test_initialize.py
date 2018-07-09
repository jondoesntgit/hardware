from hardware import fog

def test_fog():
    try:
        fog
    except NameError:
        pass
        # fog is not defined
    else:
        pass
        # fog is defined
