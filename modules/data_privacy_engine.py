# ===================================================================================
# IMPORT LIBRARIES
# ===================================================================================
import os
import re

class DataPrivacyEngine:
    #Initialise class:
    def __init__(self):
        #===================
        # ATTRIBUTES
        #====================
        # 1. phone_pattern = Regex expression for kenyan phone numbers
        self.phone_pattern = re.compile(r'(?:\+254|0)[17]\d{8}')

    #===================
    # METHODS
    #====================
    # 1.mask_phone_number - Method to mask phone numbers
    def mask_phone_number (self, input_text:str) -> dict:
        #creates a dictionary to store the pii with the values used for masking
        pii_store_phone = {}
        message_payload = input_text

        # Get a list of all phone numbers from the text input
        phone_numbers = self.phone_pattern.findall(input_text)

        #Loop through the list to get the  phone numbers store them in dictionary for later retrieval 
        #Then replace the phone number with masked data

        if phone_numbers:
            for index, phone in enumerate(phone_numbers):
                replacement = f"[masked_phone]_{index+1}"
                pii_store_phone[replacement]=phone
                message_payload_masked = message_payload.replace(phone, replacement)

            output =  {
                "compliant_payload":message_payload_masked,
                "secure_vault":pii_store_phone,
                "status":"PII Found and Masked"
            }
            return output
        output =  {
                "compliant_payload":message_payload,
                "secure_vault":None,
                "status":"No PII Found"
            }
        return output
    
    # 2.demask_phone_number - Method to mask phone numbers
    def demask_phone_number (self, input_text:str, pii_store:dict) -> str:
        message_payload = input_text
        #loop through the pii store, 

        for replacement, phone in pii_store.items():
            demasked_message_payload = message_payload.replace(replacement, phone) 
        
        return demasked_message_payload
    
privacy_engine = DataPrivacyEngine()


# =========================================================   
#CODE TESTING:
# ==========================================================
if __name__=="__main__":
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


   

    
    
    # c_pyload = output_dict["compliant_payload"]
    # print(c_pyload)
    # pii_store = output_dict["secure_vault"]
    # print(pii_store)


    # 2.unmasking
    # restored_payload = privacy_engine.demask_phone_number(c_pyload, pii_store)
    # print(restored_payload)




    







    


    
