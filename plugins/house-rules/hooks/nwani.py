"""Finds Nwani's messages that arrive while Claude is mid-turn, for the checks that count turns.

The thread records those as a queued attachment instead of a message, along with helper reports,
relays and notes. Only one whose wake carries a message from a person is Nwani's.
"""
import re

HUMAN = re.compile(r'<message\b[^>]*\bfrom="human"')


def queued_message(entry):
    """The message's text if this record entry is Nwani's message or tap arriving mid-turn, else None."""
    attached = entry.get("attachment") or {}
    prompt = str(attached.get("prompt", ""))
    if entry.get("type") == "attachment" and attached.get("type") == "queued_command" and HUMAN.search(prompt):
        return prompt
    return None
