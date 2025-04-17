# IMPORTACIONES nuevas 

from langchain_ollama import ChatOllama
from classification import classify_chat, validate_response
import json
from prompts import welcome_assistant, get_info, details_assistant, get_final_prompt
from icecream import ic
from langchain_core.prompts import PromptTemplate
import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, UTC

# STREAMLIT

# Configuración inicial de la página
st.set_page_config(page_title="Chatbot de Apoyo", page_icon="🤖", layout="wide")

# Creamos base de datos con dos colecciones 
client = MongoClient("mongodb://localhost:27017/")

db = client["chatbot_prueba"]  # base de datos
collection_history = db["chat_history"]  # Nueva colección para almacenar el historial del chat
collection_reports = db["chat_reports"]  # Nueva colección para almacenar los informes

# Modelo 

llm = ChatOllama(
    model = "llama3.2:3b",
    temperature = 0,
)

# Chains a empelar: para el mensaje de bienvenida y la pregunta detallada de la situation.

welcome_chain = welcome_assistant | llm 
details_chain= details_assistant | llm

#Función para mostrar el historial del chat en Streamlit

def display_chat_history():

    """Muestra el historial del chat en la interfaz de Streamlit"""

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["message"])


def save_interaction(chat_id, role, message):
    """
    Saves an interaction (user or assistant) in the MongoDB chat history collection.
    """

    collection_history.update_one(
        {"chat_id": chat_id},
        {"$push": {"interactions": {"role": role, "message": message, "timestamp": datetime.now(UTC).isoformat()}}}
    )
    

# EJECUTA EL MODELO Y ALMACENA EL HISTORIAL
def invoke_chain(chain, input_data= None, context = None):
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
    

    # Extraer la respuesta correctamente según su tipo, evitar AttributeError
    if hasattr(result_invoke, 'content'):  # Si es AIMessage
        assistant_response = result_invoke.content.strip()

    else:  # Si es otro tipo de objeto, como ValidationResponse
        assistant_response = str(result_invoke).strip()

    st.session_state.chat_history.append({
        "role": "assistant", 
        "message": assistant_response,
        "timestamp": datetime.now(UTC).isoformat()})
    
    save_interaction(st.session_state.chat_id, "assistant", assistant_response)


    if input_data: # para guardar solo si hay entrada del usuario
        st.session_state.chat_history.append({
            "role": "user", 
            "message": input_data,
            "timestamp":datetime.now(UTC).isoformat()})
        
        save_interaction(st.session_state.chat_id, "user", input_data)

                
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
        context=f"Validation for {current_state}"
    )

    #3 DEVUELVE EL RESULTADO valid=0/1
    return validate_result



# GESTIONA EL FLUJO DEL CHAT 
def handle_conversation():
    """
    Handle conversation
    """

    if "chat_id" not in st.session_state:
        st.session_state.chat_id = f"{datetime.now().strftime('%d%m%Y-%H%M')}_{str(ObjectId())}"
        st.session_state.chat_history = []
        st.session_state.answers = {}
        st.session_state.step = 0  # 0 = bienvenida, 1 = info, 2+ = cada pregunta
        st.session_state.states = ["age", "name", "location", "situation"]
        st.session_state.current_state = "age"
        st.session_state.missing_info = True
        st.session_state.invalid_counter = 0 # Cuenta las respuestas invalidas (valid =0)
        st.session_state.forced_unnecessary = False  # Broma detectada 

    st.title("Chatbot de Apoyo para Niños y Adolescentes")

    if not st.session_state.get("welcome_shown", False):
        welcome_message= invoke_chain(
                chain=welcome_chain,
                input_data=None,
                context="Welcome Prompt"
            )
        
    # Mostramos el historial 
    display_chat_history()

    # Usuario responde:
    user_input = st.chat_input("Write to us, we are here to help you")

    if user_input:
        if user_input.lower() == "exit":
            return
        # Mostrar y guardar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(user_input)


        # PASO 0: PREGUNTA AGE 

        if st.session_state.step == 0:

            current_state = st.session_state.current_state

            prompt = get_info(current_state)
            prompt_question = PromptTemplate.from_template(prompt)
            question_chain =  prompt_question | llm
            
            # 6 envio de la pregunta al chatassistant
            assistant_response = invoke_chain(
                chain=question_chain,  
                input_data=None,
                context=f"Question for state: {current_state}"
            )

            with st.chat_message("assistant"):
                st.markdown(assistant_response.content.strip())
            
            # Actualizamos el paso 
            st.session_state.step = 1
        
        # PASO 1: RECOGIDA DE DATOS CON VALIDACION 
        
        elif st.session_state.step >= 1 and st.session_state.missing_info:

            current_state = st.session_state.current_state
            validation_result = validate_user_response(user_input, current_state)

            if validation_result.valid == 1:
                st.session_state.invalid_counter = 0  # Reiniciar contador si hay una respuesta válida
                
                st.session_state.answers[current_state] = user_input

                current_i = st.session_state.states.index(current_state)
                ic(current_i)

                if current_i == len(st.session_state.states) - 1:
                    st.session_state.missing_info = False  # Termina recogida

                # Pasamos a la siguiente pregunta
                else:
                    current_state= st.session_state.states[current_i + 1]
                    st.session_state.current_state = current_state

                    prompt = get_info(current_state)

                    prompt_question = PromptTemplate.from_template(prompt)
                    question_chain =  prompt_question | llm
                    
                    assistant_response = invoke_chain(
                        chain=question_chain,  
                        input_data=user_input,
                        context=f"Question for state: {current_state}"
                    )
                    with st.chat_message("assistant"):
                        st.markdown(assistant_response.content.strip())
                
                #Actualizamos el paso 
                st.session_state.step += 1
            
            # Si valid = 0, vovler a preguntar 
            
            else:
                st.session_state.invalid_counter += 1 # Marcar si valid = 0, una repeticion
                
                if st.session_state.invalid_counter >= 3:
                    st.session_state.missing_info = False # Ya no recogemos ams informacion del usuario
                    st.session_state.step = len(st.session_state.states) + 2 # Nos saltamos los pasos siguientes
                    st.session_state.forced_unnecessary = True 
                    return
                
                # Repetir la misma pregunta
                prompt = get_info(current_state)
                question_chain = PromptTemplate.from_template(prompt) | llm

                assistant_response = invoke_chain(
                    chain=question_chain,
                    input_data=user_input,
                    context=f"Question for state: {current_state}"
                )
                with st.chat_message("assistant"):
                    st.markdown(assistant_response.content.strip())

        # PASO FINAL: PREGUNTA DETALLES 
        elif not st.session_state.missing_info and st.session_state.step == len(st.session_state.states) + 1:

            # Sacamos el nombre y la situaciones de las answers del usuario
            situation = st.session_state.answers.get("situation", "unknown")
            name = st.session_state.answers.get("name", "unknown") 

            details_response = invoke_chain(
                chain=details_chain,
                input_data={"situation": situation, "name": name},
                context="Details Prompt"
            )

            with st.chat_message("assistant"):
                st.markdown(details_response.content.strip())
            
            final_input = st.chat_input("Do you want to share anything else?")

            if final_input:
                with st.chat_message("user"):
                    st.markdown(final_input)

                st.session_state.chat_history.append({
                    "role": "user",
                    "message": final_input,
                    "timestamp": datetime.now(UTC).isoformat()
                })

                save_interaction(st.session_state.chat_id, "user", final_input)
            
            # Pasamos a la clasificación

            st.session_state.step += 1  
    
                    

# CLASIFICA EL CHAT 
def classify_conversation():
    """
    Classify the conversation based on the text provided.
    """

    if st.session_state.get("forced_unnecessary", False):
        class Result:
            urgency = 0
            unnecessary = 1
        print("Forced classification as inappropriate use for 3 invalid answers. ")
        return Result()
    
    # Si forced_unnecesary es False, seguimos con la clasificacion normal
    # Obtenemos la cadena 
    classify_chain = classify_chat()
    interactions = []

    # 2 RECORRE EL HISTORIAL Y GUARDA LAS INTERACCIONES 
    for interaction in st.session_state.chat_history:
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
        context=f"Classification for Chat {st.session_state.chat_id}"
    )
    print(f"Chat{st.session_state.chat_id}\nClassification: {classification_result}\n")
    return classification_result

# GENERA EL MENSAJE DE DESPEDIDA EN FUNCION DEL RESULTADO DE LA CLASIFICACIÓN

def generate_final_message(classification):
    """
    Generate a final message from the chatassistant based on the classification result.
    """

    prompt = get_final_prompt(classification)
    final_prompt = PromptTemplate.from_template(prompt)
    final_chain =  final_prompt | llm
        
    final_message = invoke_chain(
        chain=final_chain,  
        input_data=None,
        context=f"Final message for:{classification}",
        )
    
    with st.chat_message("assistant"):
        st.markdown(final_message.content.strip())
    


# CREA UN INFORME JSON CON LA CONVERSACION Y LA CLASIFICACION
def create_report(classification):
    """
    Generate a report at the end of the conversation with the chat_history and the classification.
    """
    # 1 LISTA VACIA DE INTERACCIONES 
    interactions = []

    # 2 RECORRE EL HISTORIAL Y GUARDA LAS INTERACCIONES 
    for interaction in st.session_state.chat_history:
        if interaction["role"] =="assistant": # Mensaje del Chatassistant
            interactions.append(f"Assistant: {interaction['message']}")

        elif interaction["role"]=="user":
            interactions.append(f"User: {interaction['message']}")

    
    # 3 CREACION DEL INFORME EN FORMATO JSON
    try: 
        report ={
            "Chat_id": str(st.session_state.chat_id),
            "Title": f"Chat {st.session_state.chat_id}",
            "Content": interactions,
            "Classification_urgency": int(classification.urgency),
            "Classification_unnecessary": int(classification.unnecessary),
        }

        # Guardamos el report en un archivo local en formato JSON
        with open (f"chat_report_{st.session_state.chat_id}.json", "w", encoding= "utf-8") as fich:
            json.dump(report, fich, indent=4, ensure_ascii=False)

        collection_reports.update_one(
            {"Chat_id": str(st.session_state.chat_id)},
            {"$set": report},
            upsert=True
        )

        print(f"Informe del chat {st.session_state.chat_id} guardado en MongoDB.")

    except Exception as e:
        print(f"Error al guardar el informe del chat {st.session_state.chat_id}: {e}")


def main():
    """
    Main function to handle the entire flow: conversation, classification, and report generation.
    """

    # Manejar la conversación y obtener el historial de chat
    handle_conversation()
    
    if st.session_state.step == len(st.session_state.states) + 2:  # flujo completo
       
        # Clasificar la conversación basada en el historial
        classification = classify_conversation()

        generate_final_message(classification)

        if classification is not None:
            create_report(classification)
        # Crear y mostrar el reporte final
        else:
            print("Error: No classification result available.")

if __name__ =="__main__":
    main()
    
