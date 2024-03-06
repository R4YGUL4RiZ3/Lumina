def load_instructions(file: str) -> str:
    with open(file, 'r') as f:
        instructions = f.read()
    return instructions
