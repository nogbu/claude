# house-rules

Nwani's automatic checks for Claude in claude.ai project threads, plus the reviewer helper.
Before Claude sends a reply or a decision card, the checks look for the mistakes listed in the
nogbu/claude repo's MANUAL.md under Automatic checks, and send Claude back to fix them. The
reviewer helper checks longer answers before they are sent. The checks only run in cloud threads
that have the nogbu/claude repo, where the rules they enforce are written.
