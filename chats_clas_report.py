from classification import create_classify_conversation
import json
from main_04 import invoke_chain
from chats_more import chat_1, chat_2, chat_3, chat_4, chat_14, chat_10, chat_11, chat_12, chat_13, chat_15, chat_5, chat_6, chat_7, chat_8, chat_9
from langchain_core.messages import AIMessage, HumanMessage


def classify_chats(chat, chat_id):
    """
    Classifies the chats in 'chats_more.py' and generates a report for each one.
    """

    classify_chain = create_classify_conversation()
    
    classification_result = invoke_chain(
        chain=classify_chain, 
        input_data={"input": str(chat)},
        chat_history=None,      
        context=f"Classification for Chat {chat_id}")
    
    print(f"Chat{chat_id}\nClassification: {classification_result}\n")
    return classification_result

        
def report_chat(classification, chat, chat_id):
    """
    Creates and saves a report for a classified chat.
    """
    interactions = []

    for interaction in chat:
        if isinstance(interaction, HumanMessage):
            interactions.append(f"User: {interaction.content}")
        elif isinstance(interaction, AIMessage):
            interactions.append(f"Chatassistant: {interaction.content}")

    formatted_chat = interactions


    report = {
        "Title": f"Chat {chat_id}",
        "Classification_urgency": classification.urgency,
        "Classification_unnecessary": classification.unnecessary,
        "Content": formatted_chat
    }
        
    with open(f"chat_{chat_id}_report.json", "w", encoding="utf-8") as fich:
        json.dump(report, fich, indent=4, ensure_ascii=False)
        
    print(f"Report generated for Chat {chat_id}")
    


def main():
    """
    Main function to classify and generate reports for all chats.
    """
    chats = {
        1: chat_1, 2: chat_2, 3: chat_3, 4: chat_4,
        5: chat_5, 6: chat_6, 7: chat_7, 8: chat_8,
        9: chat_9, 10: chat_10, 11: chat_11, 12: chat_12,
        13: chat_13, 14: chat_14, 15: chat_15
    }
    
    chat_id = int(input("Enter the chat ID:"))
    # el bucle for recorre el diccionario chats 
    #chats.items() devuelve un conjunto de pares (clave,valor) = (chat_id, chat mensajes)
    if chat_id in chats:
        classification = classify_chats(chats[chat_id], chat_id)
        if classification is not None:
            report_chat(classification, chats[chat_id], chat_id)
        else:
            print(f"Error: No classification result available for {chat_id}.")
    else:
        print("Invalid chat number.")


if __name__ == "__main__":
    main()