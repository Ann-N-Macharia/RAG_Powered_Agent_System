import traceback
from modules.data_privacy_engine import privacy_engine

while True:
    user_input = input("query: ")
    print(user_input)

    compliant_object = privacy_engine.mask_phone_number(user_input)

    compliant_input = compliant_object["compliant_payload"]
    print(compliant_input)


# #Input validation

# # #Error handling

# def div(num:float|int, den:float|int) -> float:
#     if not isinstance(num,(float,int)) or not isinstance(den,(float,int)):
#         print("Non numeric data type detected")
#         return "Non numeric data type detected"
#     try:
#         output = num/den
#         print(output)
#         return output
#     except Exception as e:
#         return print (f"Error: {e}")
    

# import traceback

# def div(num: float | int, den: float | int) -> float | str:
#     if not isinstance(num, (float, int)) or not isinstance(den, (float, int)):
#         print("Non numeric data type detected")
#         return "Non numeric data type detected"

#     try:
#         output = num / den
#         print(output)
#         return output
#     except Exception:
#         print("An error occurred:")
#         return "Division failed."
    

# div(10, 0)





