# IMPORTACIONES nuevas 

from langchain_ollama import ChatOllama
from classification import classify_chat, validate_response
import json
from prompts import welcome_assistant, get_info, details_assistant, get_final_prompt
from icecream import ic
from langchain.prompts import PromptTemplate
import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, UTC

# STREAMLIT

# Configuración inicial de la página
st.set_page_config(page_title="Chatbot de Apoyo", page_icon="🤖", layout="wide")

prompt = st.chat_input("Write to us, we are here to help you")


# Creamos base de datos con dos colecciones 
client = MongoClient("mongodb://localhost:27017/")

db = client["chatassistant_prueba"]  # nueva base de datos
collection_history = db["chat_history"]  # Nueva colección para almacenar el historial del chat
collection_reports = db["chat_reports"]  # Nueva colección para almacenar los informes

# Modelo 

llm = ChatOllama(
    model = "llama3.2:3b",
    temperature = 0,
)

welcome_chain = welcome_assistant | llm 

details_chain= details_assistant | llm

chat_history = []


#Función para mostrar el historial del chat en Streamlit


def display_chat_history(chat_history):

    """Muestra el historial del chat en la interfaz de Streamlit"""

    for message in chat_history:
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["message"])
        else:
            with st.chat_message("user"):
                st.markdown(message["message"])


# GUARDA LAS INTERACCIONES EN LA BASE DE DATOS 

def save_interaction(chat_id, role, message):
    """
    Saves an interaction (user or assistant) in the MongoDB chat history collection.
    """

    collection_history.update_one(
        {"chat_id": chat_id},
        {"$push": {"interactions": {"role": role, "message": message, "timestamp": datetime.now(UTC).isoformat()}}}
    )
    
    

# EJECUTA EL MODELO Y ALMACENA EL HISTORIAL
def invoke_chain(chain, input_data= None, chat_history=None, context = None):
    """
    Generic method to invoke chains and manage history.
    
    """
    # 1 PROCESO DE EJECUCION SEGUN EL TIPO DE ENTRADA 
    
    # Si no hay input_data y la cadena no lo requiere, hacerlo directamente
    if input_data is None:
        result_invoke = chain.invoke({})
    elif isinstance(input_data, str):
        result_invoke = chain.invoke({'input': input_data})
    else:
        result_invoke = chain.invoke(input_data)
    
    # 2 GUARDA EN EL HISTORIAL 

    # Extraer la respuesta correctamente según su tipo, evitar AttributeError
    if hasattr(result_invoke, 'content'):  # Si es AIMessage
        assistant_response = result_invoke.content.strip()

    else:  # Si es otro tipo de objeto, como ValidationResponse
        assistant_response = str(result_invoke).strip()

    if chat_history is not None:
        if input_data: # para guardar solo si hay entrada del usuario
            chat_history.append({
                "role": "user", 
                "message": input_data,
                "timestamp":datetime.now(UTC).isoformat()})
                
        chat_history.append({
            "role": "assistant", 
            "message": assistant_response,
            "timestamp": datetime.now(UTC).isoformat()})
        
    
    # 3 DEVUELVE EL RESULTADO
   
    print("Assistant: ", assistant_response)
    
    return result_invoke
    

# VERIFICA SI LA RESPUESTA DEL USUARIO ES VALIDA EN FUNCION DEL ESTADO
def validate_user_response(user_input, current_state):
    """
    Validate the user's response based on the current state and expected format.
    """

    desc = f"Validation for state: {current_state}"

    # 1 OBTIENE LA CADENA DE VALIDACION con el metodo create_validate_chain
    validate_chain = validate_response(current_state, desc)

    # 2 EJECUTA LA VALIDACION con invoke_chain
    validate_result = invoke_chain(
        chain=validate_chain,
        input_data=user_input,
        chat_history=chat_history,
        context=f"Validation for {current_state}"
    )

    #3 DEVUELVE EL RESULTADO valid=0/1
    return validate_result

# Inicializar el chat history 
if "messages" not in st.session_state:
    st.session_state.messages = []

# GESTIONA EL FLUJO DEL CHAT 
def handle_conversation():
    """
    Handle conversation
    """

    st.title("Chatbot de Apoyo para Niños y Adolescentes")

    chat_id = f"{datetime.now().strftime('%d%m%Y-%H%M')}_{str(ObjectId())}"
     
    # 1 GENERA Y MUESTRA EL MENSAJE DE BIENVENIDA 
    welcome_message= invoke_chain(
        chain=welcome_chain,
        input_data=None,
        chat_history=chat_history,
        context="Welcome Prompt"
    )

    with st.chat_message("assistant"):
        st.markdown(welcome_message.content.strip())

    collection_history.insert_one({
        "chat_id": chat_id,
        "interactions": [{"role": "assistant", "message": welcome_message.content.strip(), "timestamp": datetime.now(UTC).isoformat()}]
    })


    # 2 USUARIO INGRESA LA RESPUESTA 
    user_input = input("You: ")
    if user_input.lower() == "exit":
        return
    
    # Guardamos al respuesta del usuario en MongoDB

    save_interaction(chat_id, "user", user_input)

    # 3 INICIALIZACION DE LAS VARIABLES 
    current_state= "age"
    answers = {}
    missing_info = True


    # 4 CICLO DE PREGUNTAS Y RESPUESTAS 
    while missing_info:

        # 5 generacion pregunta
        prompt = get_info(current_state)
        prompt_question = PromptTemplate.from_template(prompt)
        question_chain =  prompt_question | llm
        
        # 6 envio de la pregunta al chatassistant
        assistant_response = invoke_chain(
            chain=question_chain,  
            input_data=user_input,
            chat_history=chat_history,
            context=f"Question for state: {current_state}"
        )
        
        # Guardamos al pregunta del assistant en MongoDB

        save_interaction(chat_id, "assistant", assistant_response.content.strip())


        # 7 USUARIO INGRESA LA RESPUESTA  
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        # Guardamos al respuesta del usuario en MongoDB

        save_interaction(chat_id, "user", user_input)

        # 8 VALIDACION DE LA RESPUESTA 
        validation_result = validate_user_response(user_input, current_state)

        # 9 SI ES VALIDA, GUARDA LA RESPUESTA 
        if validation_result.valid == 1:
           
            answers[current_state] = user_input

            
            # 10 ACTUALIZA EL ESTADO 
            states = ["age", "name", "location", "situation"]

            current_i = states.index(current_state)
            ic(current_i)
            
            if current_i == len(states)-1:
                missing_info = False # se ha recopilado toda la info
            else:
                current_state= states[current_i + 1]
    
     
    details_response= invoke_chain(
        chain=details_chain,
        input_data={"situation": answers.get("situation", "unknown")},
        chat_history=chat_history,
        context="Details Prompt"
    )

    save_interaction(chat_id, "assistant", details_response.content.strip()) 
        
        # 7 USUARIO INGRESA LA RESPUESTA  
    user_input = input("You: ")

    # Guardar la última respuesta en chat_history y MongoDB
    
    chat_history.append({
        "role": "user",
        "message": user_input})

    
    save_interaction(chat_id, "user", user_input)

    # 11 DEVUELVE EL HISTORIAL DEL CHAT 

    print("Historial de chat guardado en MongoDB en tiempo real.")
    return chat_id, chat_history 

# CLASIFICA EL CHAT 
def classify_conversation(chat_history, chat_id):
    """
    Classify the conversation based on the text provided.
    """
    # Obtenemos la cadena 
    classify_chain = classify_chat()
    interactions = []

    # 2 RECORRE EL HISTORIAL Y GUARDA LAS INTERACCIONES 
    for interaction in chat_history:
        if interaction["role"] =="assistant": # Mensaje del Assistant
            interactions.append(f"Assistant: {interaction['message']}")

        elif interaction["role"]=="user":
            interactions.append(f"User: {interaction['message']}")
    
    formatted_chat = "\n".join(interactions)

    # Ejecuta la clasificacion y develve el resultado
    classification_result = invoke_chain(
        chain=classify_chain,  
        input_data={"input": formatted_chat},
        chat_history=None,
        context=f"Classification for Chat {chat_id}"
    )
    print(f"Chat{chat_id}\nClassification: {classification_result}\n")
    return classification_result

# GENERA EL MENSAJE DE DESPEDIDA EN FUNCION DEL RESULTADO DE LA CLASIFICACIÓN

def generate_final_message(classification, chat_id, chat_history):
    """
    Generate a final message from the chatassistant based on the classification result.
    """

    prompt = get_final_prompt(classification)
    final_prompt = PromptTemplate.from_template(prompt)
    final_chain =  final_prompt | llm
        
        # 6 envio de la pregunta al chatassistant
    final_message = invoke_chain(
        chain=final_chain,  
        input_data=None,
        chat_history=chat_history,
        context=f"Final message for:{classification}",
        )
     
    save_interaction(chat_id, "assistant", final_message.content.strip())




# CREA UN INFORME JSON CON LA CONVERSACION Y LA CLASIFICACION
def create_report(classification, chat_id, chat_history):
    """
    Generate a report at the end of the conversation with the chat_history and the classification.
    """
    # 1 LISTA VACIA DE INTERACCIONES 
    interactions = []

    # 2 RECORRE EL HISTORIAL Y GUARDA LAS INTERACCIONES 
    for interaction in chat_history:
        if interaction["role"] =="assistant": # Mensaje del Chatassistant
            interactions.append(f"Assistant: {interaction['message']}")

        elif interaction["role"]=="user":
            interactions.append(f"User: {interaction['message']}")
    
    #Aqui no ahcemos el join porque queda mal estructurado, no lo veo encesario
    # formatted_chat = "\n".join(interactions)
    
    # 3 CREACION DEL INFORME EN FORMATO JSON
    try: 
        report ={
            "Chat_id": str(chat_id),
            "Title": f"Chat {chat_id}",
            "Content": interactions,
            "Classification_urgency": classification.urgency,
            "Classification_unnecessary": classification.unnecessary,
        }

        # Guardamos el report en un archivo JSON
        with open (f"chat_report_{chat_id}.json", "w", encoding= "utf-8") as fich:
            json.dump(report, fich, indent=4, ensure_ascii=False)

        # Guardamos el report en la coleccion de MongoDB
        collection_reports.update_one(
            {"Chat_id": str(chat_id)},
            {"$set": report},
            upsert=True
        )
        print(f"Informe del chat {chat_id} guardado en MongoDB.")

    except Exception as e:
        print(f"Error al guardar el informe del chat {chat_id}: {e}")


def main():
    """
    Main function to handle the entire flow: conversation, classification, and report generation.
    """

    # Manejar la conversación y obtener el historial de chat
    chat_id, chat_history = handle_conversation()

    # Clasificar la conversación basada en el historial
    classification = classify_conversation(chat_history, chat_id)

    generate_final_message(classification, chat_id, chat_history)

    if classification is not None:
        create_report(classification, chat_id, chat_history)
    # Crear y mostrar el reporte final
    else:
        print("Error: No classification result available.")

if __name__ =="__main__":
    main()
    
