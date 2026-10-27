# README notes (draft, feeds ticket 06)

Not part of the shipped README and not shipped with the plugin. One note per
chat source, written from what
`plugins/modo-ai-skills/skills/assess-my-ai-work/SKILL.md` step 0 actually does.

Common to every source
- One chat per run. It never lists, searches or skims other chats.
- It never mentions or offers coding-tool session logs unless you point to one.
- A chat needs at least 4 messages from you; otherwise it says "too short" and
  names the chat or file it looked at.
- The first line of the result says which chat or file was assessed.
- Same output and label for every source.
- If you ask for "all my chats", it says it assesses one chat at a time and
  assesses the current one.

The current chat (default)
- Reads the messages in the chat you are in, before your request to assess it.

Pasted text
- Paste the chat into your message. Your messages are the parts labelled as
  yours ("You", "Me", "User", "Human"). If it can't tell which parts are yours
  it asks.
- Opening line: "Assessment of the chat you pasted (N messages from you)".

A named past chat
- Say which chat, e.g. "assess my chat about the Q3 budget".
- It looks the chat up only by that name. With a tool that opens a chat by
  name or exact title, it opens that one chat. If the only tool is a search,
  it runs one search with your exact name for the chat and considers only
  results whose title is that name; it never reads, shows, lists or uses any
  other result's title, snippet or content.
- If several chats have that exact title it asks "which one?", listing only
  those chats (title and date), and never picks for you.
- If no chat has that title it says so, without describing anything else the
  search returned, and offers: paste the chat or point to an export file.
- If the app you are using has no way to open past chats (for example Claude
  Code), it says so and offers: paste the chat, point to an export file, or run
  the assessment inside that chat.
- Not tested against real past-chat tools (the eval environment has none);
  tested only for the "no tools" path and, via an export file, for the
  ambiguous-name path. The exact-title-only search rule is untested. Needs a manual check in the Claude app before release.

A chat export file
- Point to the file by path (for example `conversations.json` from the Claude
  data export). Name the chat you want; if the file has several chats and you
  name none, it asks which one.
- It reads only that file, and only the chosen chat inside it.
- Format tested: a list of chats, each with a title, a date and messages with
  `sender` `human` or `assistant`. This is the shape used by the Task Finder
  fixture; not checked against a current real export. Other export shapes: not
  specified.

A Claude Code session file
- In Claude Code, point to a session `.jsonl` file by path. It counts only the
  lines you typed; tool results that Claude Code stores as "user" lines are not
  counted or quoted.
- Opening line: "Assessment of the Claude Code session file <name> (N messages
  from you)".
- The location of session files on disk is deliberately not mentioned in the
  plugin; you supply the path.
