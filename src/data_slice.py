def data_slice(buffer, plc):
    try:
        level = bin(int(buffer[1:2], 16))[2:].zfill(4) + bin(int(buffer[2:3], 16))[2:].zfill(4)
        valve = bin(int(buffer[3:4], 16))[2:].zfill(4) + bin(int(buffer[4:5], 16))[2:].zfill(4)

        for j in range(1, 5):
            i = 8 - ((j - 1) * 2)
            plc.drum[j].low = level[i - 1 : i]  # L
            plc.drum[j].high = level[i - 2 : i - 1]  # H
            plc.drum[j].in_valve = valve[i - 1 : i]  # IN
            plc.drum[j].out = valve[i - 2 : i - 1]  # OUT
        
        for j in range(1, 5):
            i = 4 + ((j - 1) * 5)
            plc.drum[j].temp = float(buffer[i : i + 5])

    except Exception as error:
        print("")
        print(f"Error while data slicing: {buffer}")
        print(error)
        print("")
