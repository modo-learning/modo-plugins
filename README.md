# Modo plugins

Plugins from Modo for Claude. This repository is a plugin marketplace: add
it once, then install any plugin listed in it.

## Plugins

| Plugin | What it does |
|---|---|
| [modo-task-finder](plugins/modo-task-finder) | Finds the tasks you keep repeating across your Claude chats and suggests a skill, scheduled task or connector for each. Early development. |

## Add this marketplace

**Claude Code**

```
claude plugin marketplace add modo-learning/modo-plugins
claude plugin install modo-task-finder@modo-plugins
```

**Claude (web, desktop, Cowork)**

Open Customize, then Plugins, choose Add marketplace, and paste the
repository URL. Then install Modo Task Finder from the list.

## License

MIT. See [LICENSE](LICENSE).
