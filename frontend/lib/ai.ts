import OpenAI from "openai";
const client = new OpenAI();

async function inference(prompt: string) {
    const response = await client.responses.create({
        model: "gpt-5-nano",
        input: prompt
    });

    console.log(response.output_text);
    return response.output_text
}

export { inference }