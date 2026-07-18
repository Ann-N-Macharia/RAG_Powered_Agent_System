from modules.data_privacy_engine import privacy_engine

# 1.masking
message = "My name is Annie, my phone number is +254dfghjklkjhg"
output_dict = privacy_engine.mask_phone_number(message)
print(output_dict)

message_status = output_dict["status"]
compliant_payload = output_dict["compliant_payload"]
pii_vault = output_dict["secure_vault"]

print(message_status)
print(compliant_payload)
print(pii_vault)