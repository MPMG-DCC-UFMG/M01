
lower_case = set("o a os as e em no na nos nas de para ou do da dos das".split())

# Function to convert into title case 
def title_case(input_string): 
 
    # variable declaration for the output text  
    output_list = []
      
    # separating each word in the string 
    input_list = input_string.split(" ") 
      
    # checking each word 
    for word in input_list: 
          
        # if the word exists in the list 
        # then no need to capitalize it 
        if word in lower_case: 
            output_list.append(word)
              
        # if the word does not exist in 
        # the list, then capitalize it 
        else: 
            output_list.append(word.title())
      
    return " ".join(output_list)

