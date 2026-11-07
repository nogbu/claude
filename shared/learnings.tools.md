---
about: Tool limits and workarounds for every project
read-when: before a photo read, attachment, transcript decode, new-site fetch or background-job wait
readonly: no
---
learnings.tools  
The Google Drive and Docs learnings were dropped when Drive was disconnected (2026-10-03); git history has them.

Tool limits  
- Attachments can arrive empty (0 bytes); if so, ask me to re-attach (2026-09-30).  
- WebFetch may refuse a page I haven't linked in the conversation until I approve it; if so, ask me to paste the URL (2026-10-02).  
- Older tool results can be cleared from context in a long conversation; if a file's read result is no longer visible, re-read the file before quoting any value from it (2026-10-02).  
- After a conversation is continued from a summary, its transcript file holds only the summary and later messages, so earlier messages and tool results can't be re-read or decoded from it (2026-10-03).  
- Reddit can't be read from a cloud thread: reddit.com returns 403 to cloud servers, WebSearch refuses reddit.com results, WebFetch refuses the site, and the archive arctic-shift.photon-reddit.com is denied by the project's network settings unless added under Allowed domains (2026-10-09). Use that archive once allowed, or a Remote Control session on my computer.  
- On the 3dp cloud environment (2026-10-10), WebFetch and curl couldn't reach garden.org, greg.app, makerworld.com, printables.com or dendroboard.com (denied by network settings); WebSearch summaries still worked, so research ran on those alone.  
- On the plantagram cloud environment (2026-10-10), WebFetch can fail with DNS errors (physan.com, www3.epa.gov) when curl, after network settings allow the site, works; fetch with curl and pdftotext.  
- WebFetch can't read Amazon product pages (blocked by Amazon's robots.txt, 2026-10-02); use the maker's site or search results.  
- The transcript folder is named after the working directory (now ~/.claude/projects/-home-user-claude/) and starts with a dash, so `ls */*.jsonl` reads it as an option and fails; find the transcript with `find ~/.claude/projects -name '*.jsonl'` instead (2026-10-03).  
- A message I sent mid-turn can be shown to Claude again after the session restarts; if it was already answered, say so in a line instead of answering it again (2026-10-03).  
- A cloud thread's clone starts on its own claude/… branch, and its local main can be an old, diverged copy; don't check out main. save.sh pushes the current branch to main, so stay on the thread's branch (2026-10-04).  
- Files I attach in a thread are copied to /mnt/project-files/uploads/hearth/, named by ID with no extension (`file` shows the type) (2026-10-03).  
- Project instructions are capped at 16,000 characters and reach every new thread and the project chat; a change reaches only threads started after it (Projects docs, 2026-10-03).  
- Workflows run at most 2 agents at once on a 4-CPU thread workspace, so a big review workflow crawls; run up to 3 Agent subagents in parallel instead, or keep workflows small (2026-10-04).    
- Photos attached directly in a thread arrive compressed; for measurement, send the originals in a zip (2026-10-04).
- A thread can't start a thread in another project; give me a copy-box prompt to paste into that project's chat (2026-10-04).
- The cloud stop hook asks to commit untracked files: commit what Permission saves without asking, leave scratch files uncommitted, and list them at pkg (2026-10-04).
- A thread's workspace can reach the pip and npm registries and raw.githubusercontent.com (checked 2026-10-03). Cloud threads start without numpy's geometry partners (shapely, trimesh, manifold3d, matplotlib), but `python3 -m pip install` worked on 2026-10-06 (it was blocked on 2026-10-05); install them before running a build or scratch script (2026-10-06). On 2026-10-08 the 3dp project had no cloud environment selected, so no setup script ran; since then the session-start hook installs them in the background (shared/scripts/setup-env.sh; done when /tmp/setup-env.done exists).
- In the shell, ~ is /root, not the working directory; use absolute paths (2026-10-02).
- Waiting on a background job (2026-10-09, shelf): `while pgrep -f "name"` matches its own command line and never ends; use `wait $pid`, run the job with run_in_background (the thread is re-invoked when it exits), or watch its log for the done line with Monitor. A done pattern must match only the finished run (2026-10-10, shelf: "peak RSS" also sat on the solver's setup line, so the wait ended at once, twice); anchor pgrep at the start (`pgrep -f "^python3 name"`) or wait on the exit notice.
- Artifact pages (2026-10-10, shelf): the Artifact tool refuses .bin files, with or without contentType application/octet-stream; ship binary data as base64 in .txt files and decode it in the page with atob (projects/3dp/scripts/zoompage.py).
