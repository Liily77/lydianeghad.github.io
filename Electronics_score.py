data = "14inch l@ptop,699|16inch l@ptop,999|sm@rtphone,1099|t@blet,499|g@ming pc,1999"

device_list = data.split("|")
formatted_list = []

for device in device_list:
 device_info_list = device.split(",")
 name = device_info_list[0]
 price = int(device_info_list[1])
 new_price = int(price * 1.1);
 formatted_device = f"Device Name: {name}, Device Price: ${price}"
 corrected_formatted_device = formatted_device.replace("@","a")
 formatted_list.append(corrected_formatted_device)
 
print(formatted_list)