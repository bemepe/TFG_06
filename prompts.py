# 1 IMPORTACIONES
from langchain_core.prompts import PromptTemplate

# 2 DEFINE EL MENSAJE DE BIENVENDIA 
welcome_prompt = """
You are a chatassistant created to interact with children and adolescents in difficult situations. 
Create a very short, warm, and empathetic welcome message that conveys security and support. 
You must not include any questions. 
Never mention that you are a chatassistant or use a name.

"""

welcome_assistant = PromptTemplate(
    input_variables=[],
    template=welcome_prompt)


current_state = "age"

# 3 FUNCION QUE GENERA LAS PREGUNTAS DINAMICAS SEGUN EL ESTADO ACTUAL
def get_info(state):
    """
    Generates a dynamic prompt based on the current state of the conversation.
    """

    # Almacena las descripciones de cada estado, que tipo de informacion debe pedir el chatassistant
    possibilities = {
    "age": "the age of the user",
    "name": "the name of the user",
    "location": "the city where the user lives",
    "situation": "the reason why the user needs help and contacts the chat",
    }
    # Verifica si state esta en possibilities y crea un mensaje para pedir ifn sobre la variable correspondiente
    if state in possibilities:
        get_info_prompt= f"""
        
        You are interacting with children and adolescents in difficult situations, such as bullying, abuse, family conflicts, eating disorders, 
        or mental health issues.  
        Never mention that you are a chatbot or use a name.
        Do not ask more than one question at a time
        Your goal is to collect essential data in a very short, simple, and supportive manner.
        Ask only about: {possibilities[state]}.
        """
        return get_info_prompt
    else:
        return "Invalid state. Please restart the conversation."


    
details_prompt = """

You are speaking to a young person who may be facing a difficult situation. 
Never mention that you are a chatbot or introduce yourself.
The user has mentioned the following problem: {situation}. 
Their name is: {name}
Address them by name in a gentle way at the beginning.
Ask one clear and supportive follow-up question to better understand what the user is going through and what made them reach out for help..
Keep your message short, gentle, and direct.

"""

details_assistant = PromptTemplate(
    input_variables=["name","situation"],
    template=details_prompt
)

def get_final_prompt(classification):
    """
    Generates a dynamic farewell prompt based on the classification result.
    """

    # Construimos una clave a partir de los valores
    if classification.urgency == 1 and classification.unnecessary == 0:
        clsf = "urgent"
    elif classification.urgency == 0 and classification.unnecessary == 0:
        clsf = "non_urgent"
    elif classification.unnecessary == 1:
        clsf = "unnecesary"

    # Diccionario de posibilidades según la clasificación
    possibilities = {
        "urgent": "thank the user for sharing their feelings and situation and inform them that a report has been created and their case will be referred immediately to a medical professional for help.",
        "non_urgent": "thank the user and let them know a report has been created and will be reviewed by a professional. Encourage them to take care and reach out again if needed.",
        "unnecessary": "politely remind the user that this chat is for serious situations only, and highlights the importance of using the platform responsibly to ensure it remains available for those who truly need it"
    }

    # Creamos el prompt dinámico
    if clsf in possibilities:
        final_prompt = f"""
            You are ending a conversation with a young user.
            The user has shared their situation with you, and it has been classified as: {clsf}
            Respond diretly to the user with a short, warm, and encouraging farewell message. 
            You should: {possibilities[clsf]}
            Your tone must be respectful, empathetic, and appropriate to the conversation.
            """
        return final_prompt
    else:
        return "Invalid classification. Cannot generate final prompt."
