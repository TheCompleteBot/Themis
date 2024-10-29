import os
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class Chatbot:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_history = []
        
    def get_response(self, user_input):
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                max_tokens=150,
                temperature=0.7,
                n=1,
                stop=None,
            )
            
            # Extract the response text
            bot_response = response.choices[0].message.content
            
            # Add bot response to conversation history
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response
            
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    def clear_history(self):
        self.conversation_history = []

def main():
    # Create chatbot instance
    chatbot = Chatbot()
    
    print("Chatbot: Hello! I'm your AI assistant. Type 'quit' to exit.")
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for quit command
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Chatbot: Goodbye! Have a great day!")
            break
            
        # Get and print chatbot response
        response = chatbot.get_response(user_input)
        print("Chatbot:", response)
        
        # Add a small delay for better readability
        time.sleep(0.5)

if __name__ == "__main__":
    main()