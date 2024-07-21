from openai import OpenAI
import os

openai_api_key = os.getenv("openai_api_key")
client = OpenAI(api_key=openai_api_key)


def get_chat_response(prompt, context)->str:
    chat_template = """
    Answer the question: {} based on the context: {}

    If the answer cannot be found, write "I don't know"
    """

    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant that answers questions based on the provided context.",
        },
        {"role": "user", "content": chat_template.format(prompt, context)},
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, temperature=float(os.getenv("TEMPERATURE", 0.5))
    )
    answer = response.choices[0].message.content
    return answer


# This funciton is not used anywhere
def encode_vectors(data):
    """Encodes a list of data points into vectors using the OpenAI API.

    Args:
        data (list): A list of data points (strings) to be encoded.

    Returns:
        list: A list of encoded vectors (embeddings).
    """

    encoded_vectors = []

    # Batch data for efficiency (adjust batch_size as needed)
    batch_size = os.getenv("BATCH_SIZE_FOR_EMBEDDING", 2048)
    for i in range(0, len(data), batch_size):
        batch = data[i : i + batch_size]
        response = client.embeddings.create(input=batch, model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
        embeddings = [item["embedding"] for item in response["data"]]
        encoded_vectors.append([embeddings, "\n\n".join(batch)])

    return encoded_vectors


# This Function is not used anywhere
async def generate_embeddings(chunks):
    return encode_vectors(data=chunks)
