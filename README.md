# Modo plugins

Plugins from Modo for Claude. This repository is a plugin marketplace: add
it once, then install any plugin listed in it.

## Plugins

| Plugin | What it does |
|---|---|
| [modo-task-finder](plugins/modo-task-finder) | Finds the tasks you keep repeating across your Claude chats, estimates the time they take, and suggests a skill, scheduled task or connector for each. See its [README](plugins/modo-task-finder/README.md) for what it reads and how your data is handled. |
| [modo-ai-skills](plugins/modo-ai-skills) | Assesses how well you work with AI in one chat you choose or across several past claude.ai chats, against Modo's public rubric (for your own development, not for hiring decisions): a level, confidence and quoted evidence for five capabilities, two improvements, and a report you can export. See its [README](plugins/modo-ai-skills/README.md) for exactly what it reads and what it sends. |

## Add this marketplace

**Claude Code**

```
claude plugin marketplace add modo-learning/modo-plugins
claude plugin install modo-task-finder@modo-plugins
claude plugin install modo-ai-skills@modo-plugins
```

**Claude (web, desktop, Cowork)**

Open Customize, then Plugins, choose Add marketplace, and paste
`https://github.com/modo-learning/modo-plugins`. Then install Modo Task
Finder or Modo AI Skills from the list. Modo AI Skills can also be uploaded
as a zip; see [its README](plugins/modo-ai-skills/README.md#install).

**ChatGPT and Codex:** a single-chat build of Modo AI Skills is generated in
`openai/`; see [openai/README.md](openai/README.md).

Ready-made zips for both builds are on the
[releases page](https://github.com/modo-learning/modo-plugins/releases).
For the whole flow in one place (install on each platform, assessing one or
several chats, export and save, a demo script, and how to maintain the
plugin), read the [Modo AI Skills guide](docs/modo-ai-skills-guide.md).

## License

MIT. See [LICENSE](LICENSE).
