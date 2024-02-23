import OpenAI from "openai";

//#1 Retrieve assistant
const openai = new OpenAI({ apiKey: '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' });


const myAssistant = await openai.beta.assistants.retrieve(
    "asst_7XRIJqxAAoxTOV6vdMXvkYMF"
);



// #2 Create a Thread
const thread = await openai.beta.threads.create();


// #3 Create a Message
let message = await openai.beta.threads.messages.create(
    thread.id,
    {
        role: "user",
        content: "Looking for dog-friendly places?"
    }
);

// #4 Run assistant
let run = await openai.beta.threads.runs.create(
    thread.id,
    {
        assistant_id: myAssistant.id
    }
);


// #5 Poll run status till it's completed
let runStatus = await openai.beta.threads.runs.retrieve(thread.id, run.id);
while (runStatus.status !== "completed") {
    await new Promise(resolve => setTimeout(resolve, 1000));
    runStatus = await openai.beta.threads.runs.retrieve(thread.id, run.id);
}

// #6 Display the assistant's response
let messageList = await openai.beta.threads.messages.list(
    thread.id
  );

let messages = messageList.data.map(message => message.content[0].text);

// #7 Create another Message
message = await openai.beta.threads.messages.create(
    thread.id,
    {
        role: "user",
        content: "Amsterdam, no specifics"
    }
);

run = await openai.beta.threads.runs.create(
    thread.id,
    {
        assistant_id: myAssistant.id
    }
);

runStatus = await openai.beta.threads.runs.retrieve(thread.id, run.id);
while (runStatus.status !== "completed") {
    await new Promise(resolve => setTimeout(resolve, 1000));
    runStatus = await openai.beta.threads.runs.retrieve(thread.id, run.id);
}

messageList = await openai.beta.threads.messages.list(
    thread.id
  );

messages = messageList.data.map(message => message.content[0].text);

for (const message of messages) {
    console.log(message);
}