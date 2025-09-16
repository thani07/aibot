from flask import Flask, request, jsonify, render_template
import json
import os
from flasgger import Swagger
from flask_cors import CORS
# import a model from transformers
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

with open("diseases.json", "r", encoding="utf-8") as f:
    disease_data = json.load(f)

app = Flask(__name__)
swagger = Swagger(app)
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://preview--wellness-bot-pro.lovable.app",
            "http://172.16.37.82:5000"
        ]
    }
})

# Load model and tokenizer
# You can choose a smaller model to run on your machine, e.g. "gpt2", or a “chatglm”, or any instruction-tuned model.
MODEL_NAME = "gpt2"  
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

@app.after_request
def after_request(response):
    print("Request Origin:", request.headers.get("Origin"))
    return response


@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    """
    Chat with the health assistant
    ---
    tags:
      - Chat
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "What are the symptoms of diabetes?"
    responses:
      200:
        description: Response from the AI or disease knowledge base
        schema:
          type: object
          properties:
            response:
              type: string
              example: "Symptoms: frequent urination, excessive thirst, fatigue"
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"response": "Invalid request: JSON body expected."}), 400

    user_message = data.get("message", "").strip()
    if user_message == "":
        return jsonify({"response": "Please type a question or symptom to begin."})

    lower_msg = user_message.lower()
    for disease_key, info in disease_data.items():
        if disease_key in lower_msg:
            resp = ""
            symptoms = info.get("symptoms")
            if symptoms:
                resp += "Symptoms: " + ", ".join(symptoms) + "\n"
            prevention = info.get("prevention")
            if prevention:
                resp += "Prevention: " + ", ".join(prevention) + "\n"
            treatment = info.get("treatment")
            if treatment:
                resp += "Treatment: " + treatment
            return jsonify({"response": resp})

    # Use local model if no disease key matched
    # Build a prompt
    prompt = (
        "You are a helpful public health assistant. Provide a concise, evidence-based answer. "
        "If asked for diagnosis, advise to seek a doctor.\n\nUser question: "
        + user_message
    )

    try:
        # generate a response
        # Depending on model size, this might be slow / resource heavy
        gen = generator(prompt, max_length=200, num_return_sequences=1, do_sample=True, temperature=0.7)
        answer = gen[0]["generated_text"]
        # Optionally trim the leading prompt part, keep only the model’s reply
        # For example, remove the prompt from answer:
        if answer.startswith(prompt):
            answer = answer[len(prompt):].strip()
        if not answer:
            answer = "Sorry, I don't have a good answer right now."
        return jsonify({"response": answer})
    except Exception as e:
        print("Error generating:", e)
        return jsonify({"response": "Sorry, local AI service unavailable."})

if __name__ == "__main__":
    # you may want to turn off debug or set host
    app.run(host="0.0.0.0", port=5000, debug=True)
