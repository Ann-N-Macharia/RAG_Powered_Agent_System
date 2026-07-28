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
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

    #===================
    # METHODS
    #====================
    # 1.mask_phone_number - Method to mask phone numbers
    def mask_pii (self, input_text:str) -> dict:
        #creates a dictionary to store the pii with the values used for masking
        pii_store = {}
        message_payload = input_text

        # Get a list of all phone numbers from the text input
        phone_numbers = self.phone_pattern.findall(input_text)
        emails = self.email_pattern.findall(input_text)

        #Loop through the list to get the  phone numbers store them in dictionary for later retrieval 
        #Then replace the phone number with masked data

        if phone_numbers or emails:
            all_pii = phone_numbers+emails
            for index, pii in enumerate(all_pii):
                if re.match(self.phone_pattern, pii):
                    replacement = f"[masked_phone]_{index+1}"
                    pii_store[replacement]=pii
                    message_payload = message_payload.replace(pii, replacement)
                else:
                    replacement = f"[masked_email]_{index+1}"
                    pii_store[replacement]=pii
                    message_payload = message_payload.replace(pii, replacement)

            message_payload_masked = message_payload

            output =  {
                "compliant_payload":message_payload_masked,
                "secure_vault":pii_store,
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
    def demask_pii (self, input_text:str, pii_store:dict) -> str:
        message_payload = input_text
        #loop through the pii store, 

        for replacement, pii in pii_store.items():
            message_payload = message_payload.replace(replacement, pii) 
        demasked_message_payload = message_payload
        
        return demasked_message_payload
    



# =========================================================   
#CODE TESTING:
# =========================================================
if __name__=="__main__":
    privacy_engine = DataPrivacyEngine()

    # 1.masking
    message = "My name is Annie, my phone number is +254721950675 and email is am@gmail.com"
    output_dict = privacy_engine.mask_phone_number(message)
    

    message_status = output_dict["status"]
    compliant_payload = output_dict["compliant_payload"]
    pii_vault = output_dict["secure_vault"]

    print(message_status)
    print(compliant_payload)
    print(pii_vault)

    main_message = privacy_engine.demask_phone_number (compliant_payload, pii_vault)
    print(main_message)

   

    
    
  



    







    


    
