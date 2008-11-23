# -*- coding: utf-8 -*-
"""
    hgchangelog
    ~~~~~~~~~~~

    Mercurial extension to read commit message from changelog.

    Usage: activate the extension and set the name of your changelog in hgrc::

        [extensions]
        hgchangelog = path/to/hgchangelog.py

        [changelog]
        filename = CHANGES

    Then, committing without a given message or logfile will check if the
    changelog is included in the commit. If it is, the commit message shown
    in the editor will default to all text added to the changelog.

    :copyright: 2008 by Georg Brandl.
    :license: BSD.
"""

from mercurial import commands, cmdutil, extensions, patch

def new_commit(orig_commit, ui, repo, *pats, **opts):
    if opts['message'] or opts['logfile']:
        # don't act if user already specified a message
        return orig_commit(ui, repo, *pats, **opts)

    # check if changelog changed
    logname = ui.config('changelog', 'filename', 'CHANGES')
    if pats:
        match = cmdutil.match(repo, pats, opts)
        if logname not in match:
            # changelog is not mentioned
            return orig_commit(ui, repo, *pats, **opts)
    logmatch = cmdutil.match(repo, [logname], {})
    # get diff of changelog
    log = []
    for chunk in patch.diff(repo, None, None, match=logmatch):
        for line in chunk.splitlines():
            # naive: all added lines are the changelog
            if line.startswith('+') and not line.startswith('+++'):
                line = line[1:].strip()
                if line: log.append(line)
    log = '\n'.join(log)
    # strip bullet points and whitespace on the left
    log = log.lstrip('*- \t')
    # always let the user edit the message
    opts['force_editor'] = True
    opts['message'] = log
    return orig_commit(ui, repo, *pats, **opts)


def uisetup(ui):
    if not hasattr(extensions, 'wrapcommand'):
        return # doesn't work as nicely on old hg versions
    extensions.wrapcommand(commands.table, 'commit', new_commit)
