"""
Model loading and text generation for Qwen 2.5 7B Instruct.

Usage:
    from modules.model import load_model, generate

    model, tokenizer = load_model(quantize=True)
    output = generate(model, tokenizer, "Translate: Hello")
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def load_model(
    model_name: str = DEFAULT_MODEL,
    quantize: bool = True,
    device: str = "auto",
):
    """
    Load Qwen 2.5 7B Instruct with optional 4-bit quantization.

    Args:
        model_name: HuggingFace model ID
        quantize: if True, use 4-bit NF4 quantization (needed for 8-12GB VRAM)
        device: device map passed to from_pretrained ("auto", "cuda", "cpu")

    Returns:
        (model, tokenizer)
    """
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if quantize:
        print("Using 4-bit NF4 quantization (bitsandbytes)...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map=device,
        )
    else:
        print("Loading in bfloat16 (no quantization)...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map=device,
        )

    model.eval()
    print("Model ready.")
    return model, tokenizer


def generate(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 256,
    temperature: float = 0.1,
) -> str:
    """
    Generate text from a plain-text prompt using Qwen's chat template.

    Args:
        model: loaded model
        tokenizer: loaded tokenizer
        prompt: user message string
        max_new_tokens: max tokens to generate
        temperature: sampling temperature (0.1 = near-greedy)

    Returns:
        Generated text string (without the prompt)
    """
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode only the newly generated tokens
    new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def gpu_info() -> dict:
    """Return GPU memory info for the notebook hardware section."""
    if not torch.cuda.is_available():
        return {"available": False}

    props = torch.cuda.get_device_properties(0)
    return {
        "available": True,
        "name": props.name,
        "total_vram_gb": round(props.total_memory / 1e9, 1),
        "cuda_version": torch.version.cuda,
        "torch_version": torch.__version__,
    }
