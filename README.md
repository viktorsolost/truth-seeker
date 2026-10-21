# Truth Seeker

A skill for Claude Code and Codex that shows you what's really built in your repo.

For people who build with AI agents and need to know what's actually done.

Docs drift. READMEs promise features nobody wired up, scheduled jobs get installed and never run, and dead code keeps running. Truth Seeker reads the whole repo, runs the tests, follows the code and checks the logs, then gives every part a verdict you can trust:

- **LIVE**: exists, used, and proven by a real run or test.
- **PARTIAL**: exists but isn't proven end to end (never ran, failing, untested).
- **NONE**: planned or documented, but there's no code.
- **GHOST**: still there, doing nothing anyone uses.

Where the docs and reality disagree, it says so and points to the file that proves it.

▶ [Watch the launch video](media/truth-seeker-launch.mp4)

## What you get

One HTML page with three tabs:

1. **System Doc**: what exists, how it fits together, what's proven, what contradicts the docs, what's left. Plain English first, technical detail after.
2. **Mind Map**: the project left to right, from where the work starts to where it ends. Every part is a node, coloured by kind, with a status dot.
3. **Current State**: the real workflow top to bottom, each stage badged LIVE, PARTIAL or NONE, with a coverage score.

## Install

Copy the `truth-seeker` folder into your agent's skills folder:

```sh
git clone https://github.com/viktorsolost/truth-seeker
cp -r truth-seeker/truth-seeker ~/.claude/skills/   # Claude Code
cp -r truth-seeker/truth-seeker ~/.codex/skills/    # Codex
```

Restart the agent. Python 3 is the only requirement for building the page; the Mind Map loads d3 and the fonts from CDNs, so viewing it needs a network connection.

**What it costs:** it runs every test suite and probes local services, so it needs an agent with access to your machine (not a web sandbox), and a full audit takes a while and a fair amount of tokens. Anything it can't check is listed under "checks not done" instead of being guessed.

## Use

In a repo, ask your agent:

> truth seeker: map this repo

or "what's really built here?". It writes `docs/<repo>.content.html` (the source) and `docs/<repo>.html` (the page). Run it again later and ask it to "refresh the badges"; it keeps the layout and updates the verdicts.

## Fonts

The page uses Inter Tight, Source Serif 4 and JetBrains Mono from Google Fonts. To embed your own fonts, set `TRUTH_SEEKER_FONTS` to a folder with `sans.woff2` and/or `serif.woff2`. Only embed fonts whose licence allows it if you share the page.

## License

MIT
