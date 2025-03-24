def hex_to_binary(hex_digit):
    try:
        binary_digit = bin(int(hex_digit, 16))[2:].zfill(4)
        return binary_digit
    except Exception as error:
        print("Error while hex -> bin:", error)
        return None
