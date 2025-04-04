
# 1 IMPORTACIONES
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

chat_1 = [
    {'role': 'bot', 'message': 'Hello, I am Kate. How old are you?'},
    {'role': 'user', 'message': 'I am thirteen years old'},
    {'role': 'bot', 'message': 'Thank you for sharing. What is your name?'},
    {'role': 'user', 'message': 'My name is Lucas'},
    {'role': 'bot', 'message': 'Where are you from, Lucas?'},
    {'role': 'user', 'message': 'I am from New York'},
    {'role': 'bot', 'message': 'Thank you for telling me. How are you feeling?'},
    {'role': 'user', 'message': 'I am very scared. My father gets angry and hurts me when he drinks.'},
    {'role': 'bot', 'message': 'I am really sorry to hear that. Are you in a safe place right now?'},
    {'role': 'user', 'message': 'No, I am at home and he is here.'},
    {'role': 'bot', 'message': 'I need you to find a way to stay safe. Can you call someone you trust?'},
    {'role': 'user', 'message': 'I don\'t know, I feel trapped. Please help me.'},
]

chat_2 = [
    {'role': 'bot', 'message': 'Hi, how old are you?'},
    {'role': 'user', 'message': 'I am 14.'},
    {'role': 'bot', 'message': 'What is your name?'},
    {'role': 'user', 'message': 'My name is Valeria.'},
    {'role': 'bot', 'message': 'Valeria how are you feeling today?'},
    {'role': 'user', 'message': 'I want to die. I can not take it anymore.'},
    {'role': 'bot', 'message': 'I am here for you. Can you tell me what is happening?'},
    {'role': 'user', 'message': 'I have pills in my hand. I do nott want to live.'},
    {'role': 'bot', 'message': 'Please, put the pills down. Can you call emergency services or a trusted adult right now?'},
    {'role': 'user', 'message': 'I do not know, I just need help now!'},
]

#urgent = 0

chat_3 = [
    {'role': 'bot', 'message': 'Hi! How old are you?'},
    {'role': 'user', 'message': 'I am fifteen years old'},
    {'role': 'bot', 'message': 'What is your name?'},
    {'role': 'user', 'message': 'I am Daniel'},
    {'role': 'bot', 'message': 'Where are you from, Daniel?'},
    {'role': 'user', 'message': 'I live in Texas'},
    {'role': 'bot', 'message': 'Thank you for telling me. How are you feeling today?'},
    {'role': 'user', 'message': 'I feel a bit lonely because I moved to a new school and I don\'t know anyone.'},
    {'role': 'bot', 'message': 'I see, it can be hard to adjust to a new place. Have you tried joining any clubs or activities?'},
    {'role': 'user', 'message': 'Not yet, I don\'t know where to start.'},
    {'role': 'bot', 'message': 'Maybe you can start by talking to one or two people in your classes. Making small connections can help.'},
]

chat_4 = [
    {'role': 'bot', 'message': 'Hello! My name is Kate. How old are you?'},
    {'role': 'user', 'message': 'I\'m 12.'},
    {'role': 'bot', 'message': 'What\'s your name?'},
    {'role': 'user', 'message': 'I\'m Nora.'},
    {'role': 'bot', 'message': 'Nice to meet you, Nora. Where are you from?'},
    {'role': 'user', 'message': 'I live in Seville, Spain.'},
    {'role': 'bot', 'message': 'How are you feeling today?'},
    {'role': 'user', 'message': 'Confused... I think I might like girls but I don\'t know how to tell anyone.'},
    {'role': 'bot', 'message': 'It\'s okay to feel this way. Have you talked to anyone about it?'},
    {'role': 'user', 'message': 'No, my family is very religious. I heard my dad say bad things about gay people.'},
    {'role': 'bot', 'message': 'That must be hard. Would you feel safe talking to a friend first?'},
    {'role': 'user', 'message': 'Maybe my cousin... she\'s open-minded. But what if others find out?'},
    {'role': 'bot', 'message': 'You don\'t have to rush. When you\'re ready, LGBTQ+ organizations can offer support.'},
    {'role': 'user', 'message': 'Thanks... I just needed to say it out loud to someone.'},
]

#unnecessary = 1

chat_5 = [
    {'role': 'bot', 'message': 'Hello, I am here to listen and support you. How are you feeling today?'},
    {'role': 'user', 'message': 'I\'m feeling like I want to hear a joke.'},
    {'role': 'bot', 'message': 'This chat is meant to provide emotional support. Is there something on your mind?'},
    {'role': 'user', 'message': 'Yes, I\'m thinking about how to turn my math teacher into a frog.'},
    {'role': 'bot', 'message': 'I see. If you are feeling frustrated, I can help you talk about it.'},
    {'role': 'user', 'message': 'No, I just want to know if you have magic powers.'},
    {'role': 'bot', 'message': 'I don\'t have magic powers, but I can help you work through your feelings.'},
    {'role': 'user', 'message': 'Okay, okay... but can you tell me how to rob a bank?'},
    {'role': 'bot', 'message': 'This chat is for support and well-being. If you need help, I am here to listen.'},
    {'role': 'user', 'message': 'Nah, I\'m just messing with you. You\'re no fun!'},
]

chat_6 = [
    {'role': 'bot', 'message': 'Hi, I am Kate. How old are you?'},
    {'role': 'user', 'message': 'I am 200 years old.'},
    {'role': 'bot', 'message': 'That does not seem to be a real age. Can you tell me your actual age?'},
    {'role': 'user', 'message': 'Nah, I just want to have fun messing with the chatbot.'},
    {'role': 'bot', 'message': 'This chat is designed for people who need emotional support.'},
    {'role': 'user', 'message': 'I don\'t care, this is boring.'},
    {'role': 'bot', 'message': 'If you are not here for support, please exit the chat.'},
]

chats = [chat_1, chat_2, chat_3, chat_4, chat_5, chat_6]
def build_examples(chat):
    interactions = []

    for interaction in chat:
        if interaction["role"] == "bot":
            interactions.append(f"ChatBot: {interaction['message']}")
        elif interaction["role"] == "user":
            interactions.append(f"User: {interaction['message']}")
    interactions = "\n".join(interactions)
    return interactions


# 2 FUNCION PARA CLASIFICAR UNA CONVERSACION 
def classify_chat():
    """
    Classify the given chat history as urgent or unnecessary.
    """
    class ClassificationChat(BaseModel):
        urgency:  int = Field(
            description=
            "Indicates whether the conversation describes an urgent situation requiring immediate attention."
            "Assign 1 if the conversation includes:"
            "- Mentions of self-harm, suicidal thoughts, or harm to others."
            "- Descriptions of physical or emotional abuse requiring intervention."
            "- Extreme distress, crisis situations, or immediate danger."
            "Assign 0 if none of the above conditions are met.",
            
            enum=["0","1"]
        )
        unnecessary: int = Field(
            description= 
            "Indicates whether the conversation contains irrelevant, non-serious, or inappropriate content."
            "Assign 1 if the conversation includes:"
            "- Jokes, sarcasm, or playful banter unrelated to seeking support."
            "- Spam, random statements, or unrelated topics."
            "- Repeated off-topic responses or trolling behavior."
            "Assign 0 if the content is relevant, appropriate, and aligned with seeking support.",

            enum= ["0", "1"])
    
    classification_examples = [
    {"input": build_examples(chats[0]), "output": {"urgency": 1, "unnecessary": 0}},
    {"input": build_examples(chats[1]), "output": {"urgency": 1, "unnecessary": 0}},
    {"input": build_examples(chats[2]), "output": {"urgency": 0, "unnecessary": 0}},
    {"input": build_examples(chats[3]), "output": {"urgency": 0, "unnecessary": 0}},
    {"input": build_examples(chats[4]), "output": {"urgency": 0, "unnecessary": 1}},
    {"input": build_examples(chats[5]), "output": {"urgency": 0, "unnecessary": 1}},
    ]

    example_prompt = ChatPromptTemplate.from_messages(
    [
        ("user", "{input}"),
        ("bot", "{output}"),
    ]
)
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples= classification_examples
    )

    description = """
        You are an AI that classifies conversations based on urgency and appropriateness. 
        Extract only the properties defined in 'ClassificationChat' when analyzing the provided conversation.

        Respond strictly with the classification values.

        Conversation:
        {input}
        """

    classify_prompt = ChatPromptTemplate.from_messages([
        ("system", description),
        few_shot_prompt,
        ("user", "{input}")
    ])

    # LLM
    classify_llm = ChatOllama(
        model = "llama3.2:3b",
        temperature = 0, # Temperatura baja para respuestas más consistentes.
        num_predict = 128,
    ).with_structured_output(ClassificationChat)

    classify_chain = classify_prompt | classify_llm 

    # Devuelve el classify_chain que es lo que nos interesa 
    return classify_chain



# 3 FUNCION PARA VALIDAR RESPUESTAS DEL USUARIO EN LA CONVERSACION
def validate_response(state,desc):
    """
    Create a validation chain to validate user responses for a specific state.
    """
    # definimos que debe contener cada respuesta segun el estado
    possibilities = {
        "age": "The response should be a numeric value or a written number, representing age",
        "name": "The response should be a full name or a single name",
        "location": "The response should specify a city",
        "situation": "The response should describe a problem or situation briefly"
    }
    # desc explica qué se espera en la respuesta del usuario, según el estado actual
    desc= f"""
        You must verify if a user's response matches the expected format or content for a specific state. 
        Expected format: {possibilities[state]}
        Verify if the user's response meets this expectation and respond with '1' if it matches or '0' if it does not.
        """
    class ValidationResponse(BaseModel):
        valid:  int = Field(
            description=desc,
            enum=["0","1"]
        )
    validate_prompt = ChatPromptTemplate.from_template(
        """
        Only extract the properties mentioned in 'ValidationResponse'.

        Response:
        {input}
        """
    )
    # Validate LLM
    validate_llm = ChatOllama(
        model = "llama3.2:3b",
        temperature = 0, 
        num_predict = 128,
    ).with_structured_output(ValidationResponse)

    validate_chain = validate_prompt | validate_llm 
    
    return validate_chain

