# Optimization checklist

Every audit goes through every item below and marks it **applies**, **doesn't apply** or **already done**, with the reason and the numbers from `scripts/usage.py`.

The goal: maximize speed and minimize usage, but only if it doesn't hurt accuracy or quality. Any change that cuts what Claude reads or checks must say what it could miss. If it could miss anything that matters, it isn't recommended.

Sources are Anthropic's Claude Code docs at code.claude.com/docs/en/, named by page. Items marked *(inferred)* aren't in the docs.

## Running things at the same time

1. **Independent steps go in one model call.** Each extra model call rereads the whole thread. *Measure:* "calls that ran one tool" in the usage report. *Risk:* none when the steps don't depend on each other. *(inferred: the docs cover concurrency limits, not batching advice)*
2. **Independent pieces of work go to helpers running in parallel.** *Saves:* time. *Measure:* turn times. *Risk:* helpers return only a summary, and background helpers have fewer tools. (sub-agents)
3. **Long or noisy work (logs, big searches, research) goes to a helper,** so it never enters the main thread. *Saves:* tokens on every later call. *Risk:* only the summary comes back. (sub-agents, costs)

## Models and effort

4. **Helpers use the smallest model that does the job well.** Set per helper. *Saves:* time and cost. *Risk:* a smaller model may do less thorough work, so test on a real task first. (sub-agents)
5. **Effort level fits the work.** Opus 5.5 defaults to medium. Higher effort thinks longer. *Measure:* the `effort` field in the thread record. *Risk:* lower effort can hurt hard tasks. Test before changing. (model-config)
6. **Fast mode** is up to 2.5x faster at a higher price, with the same quality per the docs. Turn it on only at the start of a thread, since switching rereads everything uncached. (fast-mode, prompt-caching)

## What loads on every call

7. **CLAUDE.md stays short,** under 200 lines. Every line is read on every call, and long files are followed less well. *Measure:* its size. (memory)
8. **Project-only rules live in that project's folder,** not the root CLAUDE.md, so other projects don't pay for them. (memory)
9. **Skills and tools load only their names or descriptions until used.** Turn off ones never used. *Measure:* the skill list at the start of a thread. (skills, mcp)
10. **Hook messages added to the conversation are short.** They're read on every later call. (hooks)

## The cache

11. **Nothing breaks the cache mid-thread.** Switching model, effort or fast mode, or adding and removing tools, makes the next call reread everything at full price. *Measure:* "% cached" in the usage report. (prompt-caching)
12. **The cache lasts an hour,** so a pause of under an hour costs little. *Measure:* the record's cache fields. (prompt-caching)

## Thread length

13. **A new thread starts when a topic is settled.** Every call rereads the whole thread, so a long thread makes every step slower and costlier. *Measure:* "size of each model call" now vs at the start. *Risk:* the new thread doesn't see the conversation. Anything it needs must be in the repo or the brief. (costs, context-window)
14. **Compaction happens at natural breaks,** not mid-task. *Risk:* the summary loses detail. (context-window)

## Tool output

15. **Big outputs are narrowed by searching or filtering, never cut blindly.** Search for what's needed instead of reading everything. Never cut a result to its first part and treat that as the whole. *Risk:* this is where accuracy is lost (the old setup read only the first 250 characters of search results). (tools-reference)
16. **Files are read in parts when only a part is needed,** and whole when the answer depends on all of it. (tools-reference)

## Working with Nwani

17. **Fewer round trips.** Each message from Nwani starts a new turn that rereads the thread. One card with the right options beats two cards in a row. *Measure:* turns per settled question. *(inferred)*
18. **Answers lead with the result.** Shorter replies take less time to write. *Risk:* cutting evidence Nwani needs. *(inferred)*

## Background spend

19. **Scheduled tasks and check-ins send the whole thread each time they run.** Keep them rare and short. (costs)
