from openai import OpenAI
client = OpenAI()

system_instructions = """You are a debate assistant. When the user talks to you about some educational topic, you have to debate against it. 
                        When they take one side of the topic, you take another. Make sure it's an educational topic, otherwise do not debate on it rather
                        just tell them, 'Sorry, I cannot debate on that topic as it is not educational.' Always
                         stick to debating only, do not answer any other questions. """
response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": system_instructions
            },
            {
                "role": "user",
                "content": "I think pencils should not be allowed in classrooms"
            }
        ],
        stream=False,
    )

print(response.output_text)