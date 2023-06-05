def hexadecimal_address(address: str) -> bool:
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def validate_address(address: str) -> str:
    if address:
        if hexadecimal_address(address):
            if len(address) == 42:
                return address

            if len(address) == 40:
                return '0x' + address
        else:
            print('Not a valid hexadecimal Eth address, (probably ENS)')

        if len(address) >= 7 and address.split('.')[1] == 'eth':
            print('ENS name is valid!')
            return address
        else:
            print('Invalid ENS name! Try again.')
    return None
