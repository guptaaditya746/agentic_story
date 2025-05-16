import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model and tokenizer ONCE
def load_perplexity_model(model_id="gpt2", device=None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    model = AutoModelForCausalLM.from_pretrained(model_id)
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = model.to(device)
    model.eval()

    return model, tokenizer, device

# Compute perplexity for a SINGLE story
def compute_perplexity(text, model, tokenizer, device, max_length=512):
    with torch.no_grad():
        encodings = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
            padding=True,
        ).to(device)

        input_ids = encodings.input_ids
        outputs = model(input_ids, labels=input_ids)
        loss = outputs.loss
        perplexity = torch.exp(loss)

    return perplexity.item()
