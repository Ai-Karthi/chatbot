import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE

print("Loading Qwen model...")

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=dtype).to(device)
model.eval()

print(f"Qwen model loaded successfully on {device}.")

NOT_FOUND = "I don't have that information in the TechNova handbook."


def build_prompt(context, question):
    return f"""Answer the question using ONLY the handbook context below.

RULES:
- Do not invent information, guess, or use outside knowledge.
- If the answer is not in the context, say exactly: "{NOT_FOUND}"
- Give a concise answer suitable for speech (no bullet points or markdown).

HANDBOOK CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


def get_ai_response(conversation_history, prompt):
   
    try:
        messages = conversation_history + [{"role": "user", "content": prompt}]

        formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        inputs = tokenizer(formatted, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,)

        new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        
        return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    except Exception as e:
        print("Qwen error:", e)
        return "Sorry, I was unable to generate a response."
