# Vibe Coding AI Agents: Managing the Agent Lifecycle with Agents CLI and ADK 2.0

Source: <https://codelabs.developers.google.com/agents-cli-adk-lifecycle>

## 1. Overview

This lab is part of Kaggle's **5-Day AI Agents: Intensive Vibe Coding Course with Google**. You can find the additional codelabs and resources available on the [event site](https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google).

In this codelab, you will learn how to use Agents CLI to govern the complete local development lifecycle of an AI agent. Whether you are wrapping existing Gemini models or building custom agents from scratch with the [Agent Development Kit](https://adk.dev) (ADK 2.0), Agents CLI provides the tools to scaffold, build, lint, and test your agents locally.

## What you'll learn

- How to install and set up `agents-cli` and its associated skills.
- How to scaffold a new agent project.
- The structure and key files of an ADK 2.0 graph workflow agent project.
- How to run automated linting and code cleanups.
- How to launch and use the local web playground for interactive testing with auto-reloading.

## What you need

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Node.js 18+ (if using coding agent skills)
- Antigravity IDE (install and configure from [Google Antigravity](https://antigravity.google/download))

## Prerequisites

This Codelab assumes you are comfortable with:

- Using a terminal and command line.

No prior experience with AI agents or ADK 2.0 is required!

## 2. Set up Authentication & Environment

Provide your authentication credentials for the agent to call Gemini models.

## Option 1: Gemini API Key (Google AI Studio)

If you are using a standard Gemini API key (which you can obtain from [Google AI Studio](https://aistudio.google.com/app/apikey)), export it in your IDE terminal session:

``` devsite-click-to-copy
export GEMINI_API_KEY="your_api_key_here"
export GOOGLE_GENAI_USE_ENTERPRISE=FALSE
```

## Option 2: Google Cloud Application Default Credentials

If you are using Vertex AI on Google Cloud, authenticate with Google Cloud Application Default Credentials (ADC) and set your active Google Cloud project:

``` devsite-click-to-copy
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=REPLACE-WITH-YOUR-PROJECT_ID # Replace with your project ID
export GOOGLE_CLOUD_LOCATION=REPLACE-WITH-LOCATION # Replace the location
```

## 3. Set up Agents CLI & Skills

The first step is to install the `agents-cli` tool. This tool handles the heavy lifting of agent project management.

**Note for Antigravity users:** During this codelab, Antigravity may generate implementation plans or display popups before executing commands or writing code. Be sure to review and **approve** these plans or popups to allow Antigravity to proceed with the tasks.

**Quota Tip:** If you run out of quota during testing or development, you can switch the model in Antigravity to another available model.

With Antigravity installed, run the setup command directly in your terminal.

👉 **Open a terminal and run:**

``` devsite-click-to-copy
uvx google-agents-cli setup
```

This command automatically installs:

1.  The **Agents CLI** tool globally on your system.
2.  Seven domain-specific coding assistant **skills** that Antigravity can use to help you build, scaffold, evaluate, and deploy agents. These skills are installed once globally into `~/.agents/skills/` and are automatically discovered by Antigravity.

Note: Skills are installed into `~/.agents/skills/` and picked up automatically by Antigravity. You can verify this using the `/skills` command or your Antigravity settings.

**Expected Output (trimmed):**

``` devsite-click-to-copy
█▀█ █▀▀ █▀▀ █▄ █ ▀█▀ █▀ █▀▀ █ █`
`█▀█ █▄█ ██▄ █ ▀█ █ ▄█ █▄▄ █▄ █`

`Your coding agent just got an upgrade.`

`1. Authentication`

`─────────────────`

`✓ Authenticated with Google Cloud`

`2. CLI Installation`

`───────────────────`

`▸ uv tool install google-agents-cli`

`✓ Installed google-agents-cli`

`3. Skills Installation`

`──────────────────────`

`▸ npx -y skills add https://github.com/google/agents-cli -y --all -g`

`◇ Found 7 skills`

`~/.agents/skills/google-agents-cli-adk-code`

`~/.agents/skills/google-agents-cli-deploy`

`~/.agents/skills/google-agents-cli-eval`

`~/.agents/skills/google-agents-cli-observability`

`~/.agents/skills/google-agents-cli-publish`

`~/.agents/skills/google-agents-cli-scaffold`

`~/.agents/skills/google-agents-cli-workflow`
```

## 4. Create your Agent Project

In this section, you will create a fully structured project directory using the prototype template.

👉 Prompt Antigravity:

``` devsite-click-to-copy
Use ADK 2.0 to create a new graph workflow agent project called
customer-support-agent. I don't want to deploy this agent, so you can skip
the deployment files. The workflow should act as a customer support
representative for a shipping company. It should first classify if the user
query is related to shipping (rates, tracking, delivery, returns) or
unrelated. If it is related to shipping, route to a shipping FAQ agent to
answer the question. If it is unrelated, route to a node that politely
declines to answer.
```

Antigravity automatically runs the scaffolding command (`agents-cli scaffold create customer-support-agent --prototype --yes`) and sets up the project files for you.

**Antigravity Tip:** Antigravity may initially only give you an implementation plan. If so, be sure to click or type **Proceed** to execute it. Read the output carefully and decide if you need to further prompt Antigravity if it didn't fully get to the expected output below.

## 5. Explore the Agent Code

👉 Ask Antigravity to explain the generated code:

``` devsite-click-to-copy
Read and explain the project structure of my new agent project. Walk me
through how `app/agent.py` is configured, highlighting the role of the
tools, nodes, edges, and the root Workflow.
```

In the Antigravity IDE, newly created project files and artifacts are displayed directly in the auxiliary pane (left side). You can view `app/agent.py` there, or open it from the IDE file explorer to explore the scaffolded code.

**Note:** You are now looking at the agent code that Antigravity just created. Because Antigravity generates implementations dynamically, the code in your `app/agent.py` file may be structured or formatted differently than the example snippet below. Every user's agent will look slightly different, but they should share the same main concepts. If you feel your generated script isn't adequate or is missing functionality, remember that you can keep prompting Antigravity to iterate on and refine the code!

``` devsite-click-to-copy
# app/agent.py

from __future__ import annotations

from typing import Any, Literal

from google.adk.agents.context import Context
from google.adk.apps.app import App
from google.adk.events.event import Event
from google.adk.workflow import Edge
from google.adk.workflow import Workflow
from google.adk.workflow.agents.llm_agent import LlmAgent
from google.adk.workflow.node import node
from pydantic import BaseModel
from pydantic import Field


class InquiryCategory(BaseModel):
  category: Literal['shipping', 'unrelated'] = Field(
      description=(
          'Determine if the user query is related to shipping (rates, tracking,'
          ' delivery times, returns) or unrelated.'
      )
  )


def save_query(node_input: str):
  """Saves user query in state for downstream nodes."""
  yield Event(data=node_input, state={'user_query': node_input})


categorize_agent = LlmAgent(
    name='categorize',
    model='gemini-3.1-flash-lite',
    instruction='You are an expert classifier. Categorize the user query.',
    output_key='inquiry_category',
    output_schema=InquiryCategory,
)


@node
def route_inquiry(ctx: Context, node_input: Any):
  """Routes the workflow based on the classified category."""
  category_data = ctx.state.get('inquiry_category', {})
  category = category_data.get('category', 'unrelated')
  query = ctx.state.get('user_query', '')
  yield Event(data=query, route=category)


faq_agent = LlmAgent(
    name='shipping_faq',
    model='gemini-3.1-flash-lite'',
    instruction="""You are a customer support representative for a shipping company. Answer user questions based ONLY on the shipping FAQ below. Do not answer questions outside of the FAQ.
    
    SHIPPING FAQ:
    - Rates: Standard shipping is $5.99. Express shipping is $12.99. Orders
      over $50 qualify for free standard shipping.
    - Tracking: You can track your order by entering your tracking number on
      our website's tracking page.
    - Delivery Times: Standard delivery takes 3-5 business days. Express
      delivery takes 1-2 business days.
    - Returns: We offer free returns within 30 days of delivery. Please make
      sure the item is in its original condition.
    """,
)


@node
def handle_unrelated(ctx: Context, node_input: Any):
  """Handles unrelated inquiries politely."""
  yield Event(
      data=(
          'I am sorry, I am a shipping customer support assistant and can only'
          ' answer questions related to our shipping FAQ.'
      )
  )


root_agent = Workflow(
    name='customer_support_workflow',
    edges=[
        *Edge.chain('START', save_query, categorize_agent, route_inquiry),
        (route_inquiry, faq_agent, 'shipping'),
        (route_inquiry, handle_unrelated, 'unrelated'),
    ],
)

app = App(
    name='customer_support_agent',
    root_agent=root_agent,
)
```

## Key Concepts

- **Workflow & Edges**: In ADK 2.0, agent applications are orchestrated as a graph using `Workflow`. The `edges` list defines the execution flow, chaining nodes together from `START` and enabling conditional branching based on routes (e.g., routing to `faq_agent` on `"shipping"` or `handle_unrelated` on `"unrelated"`).
- **LlmAgent**: Declarative nodes that define LLM-powered tasks with specific instructions, models, and structured outputs (`output_schema`).
- **Nodes & Context**: Python functions decorated with `@node` (or standard functions) that perform logic, access execution state via `Context`, and yield `Event` objects to pass data and routing signals along the graph.
- **Model**: \`gemini-3.1-flash-lite' is used as the default fast reasoning model.
- **App Wrapper**: The top-level `App` object wraps the root workflow. External tools like the local playground, ADK evaluation harnesses, and Agent Runtime discover and execute your workflow through this standardized `app` interface.

## 6. Automated Linting

Before running or testing your agent, it is a good practice to ensure your code is clean and formatted correctly.

👉 Prompt Antigravity:

``` devsite-click-to-copy
Run linting on my agent project to verify its health.
```

Antigravity will execute `agents-cli lint` behind the scenes to run pre-configured checks, verifying imports, syntax, and formatting consistency across your files.

## 7. Interactive Testing with the Playground

The local web playground is the fastest way to verify your agent's behavior. It provides an interactive chat interface where you can chat with your agent and inspect tool executions in real-time.

👉 Prompt Antigravity:

``` devsite-click-to-copy
Launch the local development playground for my agent.
```

Antigravity will start the local development server (`agents-cli playground`). Open the provided URL (typically `http://127.0.0.1:8080/dev-ui/?app=app`) in your web browser, select the folder `app` from the dropdown to start chatting with your agent.

Start chatting with your agent in the web interface. Try asking a shipping-related question:

``` devsite-click-to-copy
How much is standard shipping?
```

Note how the workflow successfully categorizes and routes to `faq_agent` to answer. Also try asking an unrelated question to verify that the workflow routes to `handle_unrelated` and correctly declines to answer:

``` devsite-click-to-copy
What is the weather like?
```

## Test Real-Time Auto-Reloading

You can see how real-time edits to your agent are reflected in the Playground.

1.  Modify the `faq_agent` instruction in `app/agent.py` by asking Antigravity:

    ``` devsite-click-to-copy
    Modify the faq_agent instruction in app/agent.py to make the shipping rates
    response more playful and enthusiastic. Add some emojis and highlight the
    free shipping threshold.
    ```

2.  Send a new message to the agent in the playground to test the auto-reloading:

    ``` devsite-click-to-copy
    How much is standard shipping?
    ```

    The playground automatically reloads and executes your updated code in real-time without needing a server restart! You should see some emojis in the response now.

## 8. Command Line Execution

For quick tests, automation, or scripting, you can ask Antigravity to run your agent directly from the terminal.

👉 Prompt Antigravity:

``` devsite-click-to-copy
Run a CLI query asking my agent how long standard delivery takes.
```

Antigravity will execute the query command (`agents-cli run "How long does standard delivery take?"`). This runs a quick single-turn inference and prints the agent's final response along with tool execution details.

## 9. Cleanup

To avoid leaving unwanted resources in your local environment, follow these cleanup steps:

1.  **Stop Local Servers**: If your `agents-cli playground` server is still running, stop it in your terminal by pressing `Ctrl + C`.
2.  **Remove Local Project Files**: Delete the scaffolded agent project directory from your local machine.

``` devsite-click-to-copy
rm -rf customer-support-agent
```

## 10. Summary & Next Steps

Congratulations! You have successfully managed the end-to-end local development lifecycle of an AI agent using **Agents CLI** and **ADK 2.0**.

## What you learned

- **Set Up your Tools**: Installed the Agents CLI and configured domain-specific workflow skills for Antigravity.
- **Scaffolded a Project**: Created a fully structured `customer-support-agent` project using standardized templates.
- **Analyzed ADK 2.0 Structure**: Explored graph workflows, LLM agents, nodes, edges, and conditional routing.
- **Managed Local Health**: Ran automated code quality checks using `agents-cli lint`.
- **Verified Behavior**: Tested the agent interactively with real-time hot-reloading via the playground, and ran quick tests on the command line.

## What's Next?

Now that you have mastered the local development loop, here is how you can expand and productionize your agent:

- **Evaluation**: Score your agent against an evalset using `agents-cli eval run` to measure accuracy and find regressions.
- **Enterprise Cloud Scale: Deployment** & **Observability**: Package and deploy your agent to production environments like **Agent Runtime** or **Cloud Run** using `agents-cli deploy`. Set up production telemetry to stream logs and execution traces to Cloud Trace and BigQuery.

## Additional Resources

- [Agents CLI GitHub Repository](https://github.com/google/agents-cli)
- [Agent Development Kit (ADK) Documentation](https://adk.dev)
- [Agent Platform Overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform)
