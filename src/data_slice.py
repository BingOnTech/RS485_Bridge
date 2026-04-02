# hex_to_binary 함수 대신 bin 함수를 직접 사용하도록 수정
# 아직 테스트 버전
def data_slice(buffer, plc):
    try:
        level = bin(int(buffer[3:4], 16))[2:].zfill(4) + bin(int(buffer[4:5], 16))[2:].zfill(4)
        valve = bin(int(buffer[5:6], 16))[2:].zfill(4) + bin(int(buffer[6:7], 16))[2:].zfill(4)

        for j in range(1, 5):
            i = 8 - ((j - 1) * 2)
            plc.drum[j].low = level[i - 1 : i]  # L
            plc.drum[j].high = level[i - 2 : i - 1]  # H
            plc.drum[j].in_valve = valve[i - 1 : i]  # IN
            plc.drum[j].out = valve[i - 2 : i - 1]  # OUT

        for j in range(1, 5):
            i = 7 + ((j - 1) * 5)
            plc.drum[j].temp = int(buffer[i : i + 5])  # 온도

        for j in range(1, 5):
            plc.drum[j].show()  # 보여주기

    except Exception as error:
        print(f"Error while data slicing: {buffer}")
        print(error)

# 이게 기존 버전
"""
def data_slice(buffer, PLC):
    try:
        tmp = [hex_to_binary(buffer[3:4]), hex_to_binary(buffer[4:5])]
        level = tmp[0] + tmp[1]
        tmp = [hex_to_binary(buffer[5:6]), hex_to_binary(buffer[6:7])]
        valve = tmp[0] + tmp[1]

        for j in range(4):
            i = 8 - (j * 2)
            PLC.drum[j].low = level[i - 1 : i]  # L
            PLC.drum[j].high = level[i - 2 : i - 1]  # H
            PLC.drum[j].in_valve = valve[i - 1 : i]  # IN (renamed from 'in' as it's a reserved keyword in Python)
            PLC.drum[j].out = valve[i - 2 : i - 1]  # OUT

        for j in range(4):
            i = 7 + (j * 5)
            PLC.drum[j].temp = int(buffer[i : i + 5])  # 온도

        for i in range(4):
            PLC.drum[i].show()  # 보여주기

    except Exception as error:
        print(f"Error while data slicing: {buffer}")
        print(error)

def hex_to_binary(hex_digit):
    try:
        binary_digit = bin(int(hex_digit, 16))[2:].zfill(4)
        return binary_digit
    except Exception as error:
        print("Error while hex -> bin:", error)
        return None
"""