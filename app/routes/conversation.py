from flask import Blueprint, request, current_app, session, jsonify
from llm_manager import LLM_Manager
from database import Database_Manager
import json

conversation = Blueprint('conversation', __name__)

#add the route '/conversation' to the blueprint
@conversation.route('/conversation', methods = ['GET', 'POST', 'PUT'])
def manage_conversation():
    try:
        #returns conversation history
        if request.method == 'GET':
            input = request.get_json()
            db = Database_Manager(user_id = input['user_id'])

            return db.retrieve_conversations(), 200
        
        #begins a conversation
        if request.method == 'POST':
            input = request.get_json()
            context = None
            if 'context' in input:
                context = input['context']
            system_prompt = "You are a helpful assistant. Answer the questions succinctly."

            chat = LLM_Manager(
                model=current_app.config['MODEL'], 
                tokenizer=current_app.config['TOKENIZER'], 
                system_prompt=system_prompt, 
                context=context
                )
            
            response = {}
            response['output'] = chat.generate_response(input['prompt'])
            # session['messages'] = chat.messages
            db = Database_Manager(user_id = input['user_id'])
            conversation_id = db.insert_conversation(messages = chat.messages)
            
            response['conversation_id'] = conversation_id
            return json.dumps(response), 201
        
        #continues conversation
        if request.method == 'PUT':
            input = request.get_json()
            db = Database_Manager(user_id = input['user_id'])
            messages = db.retrieve_messages(conversation_id = input['conversation_id'])

            chat = LLM_Manager(
                model=current_app.config['MODEL'], 
                tokenizer=current_app.config['TOKENIZER'], 
                messages = messages
                )
            
            response = {}
            response['output'] = chat.generate_response(input['prompt'])
            db.update_conversation(messages = chat.messages, conversation_id = input['conversation_id'])

            return json.dumps(response), 201
    
    except Exception as e:
        print(str(e))
        return jsonify({"error": {"status": 500, "message": "Internal server error"}}), 500