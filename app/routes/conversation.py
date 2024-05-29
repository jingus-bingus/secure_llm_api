from flask import Blueprint, request, current_app, session
from llm_manager import LLM_manager
import json

conversation = Blueprint('conversation', __name__)

#add the route '/conversation' to the blueprint
@conversation.route('/conversation', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def manage_conversation():
    try:
        #returns conversation history
        if request.method == 'GET':
            return session['messages'], 200
        
        #begins a conversation
        if request.method == 'POST':
            input = request.get_json()
            context = None
            if 'context' in input:
                context = input['context']
            system_prompt = "You are a helpful assistant. Answer the questions succinctly."

            chat = LLM_manager(
                model=current_app.config['MODEL'], 
                tokenizer=current_app.config['TOKENIZER'], 
                system_prompt=system_prompt, 
                context=context
                )
            
            response = {}
            response['output'] = chat.generate_response(input['prompt'])
            session['messages'] = chat.messages

            return json.dumps(response), 201
        
        #continues conversation
        if request.method == 'PUT':
            input = request.get_json()
            
            chat = LLM_manager(
                model=current_app.config['MODEL'], 
                tokenizer=current_app.config['TOKENIZER'], 
                messages = session['messages']
                )

            response = {}
            response['output'] = chat.generate_response(input['prompt'])
            session['messages'] = chat.messages

            return json.dumps(response), 201


            





    
    except Exception as e:
        print(str(e))
        return jsonify({"error": {"status": 500, "message": "Internal server error"}}), 500