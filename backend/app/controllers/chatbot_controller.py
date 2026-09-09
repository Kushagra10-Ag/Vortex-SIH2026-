from app.services import chatbot_service

def get_response(data):
    return chatbot_service.get_response(data)