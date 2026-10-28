# Modo plugins

Plugins from Modo for Claude. This repository is a plugin marketplace: add
it once, then install any plugin listed in it.

## Plugins

| Plugin | What it does |
|---|---|
| [modo-task-finder](plugins/modo-task-finder) | Finds the tasks you keep repeating across your Claude chats, estimates the time they take, and suggests a skill, scheduled task or connector for each. See its [README](plugins/modo-task-finder/README.md) for what it reads and how your data is handled. |
| [modo-ai-skills](plugins/modo-ai-skills) | Assesses how well you work with AI in one chat you choose, against Modo's public rubric: a level, confidence and quoted evidence for five capabilities, two improvements, and a report you can export. See its [README](plugins/modo-ai-skills/README.md) for exactly what it reads and what it sends. |

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
Finder from the list. Modo AI Skills is installed from the same list.

**Testing Modo AI Skills before it merges:** it is in review on the branch
`modo-ai-skills-phase0` ([pull request #1](https://github.com/modo-learning/modo-plugins/pull/1)).
See [its README](plugins/modo-ai-skills/README.md#while-its-in-review-before-its-on-main)
for how to install it from the branch (Claude Code) or upload it as a zip
(claude.ai, desktop and Cowork).

## License

MIT. See [LICENSE](LICENSE).
