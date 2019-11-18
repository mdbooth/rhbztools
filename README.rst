======================
Red Hat Bugzilla Tools
======================

Useful tools for working with Red Hat's Bugzilla instance.

Authentication
==============

Authentication is exclusively via Bugzilla API key. To generate an API key:

* Log in to bugzilla, and navigate to:
  https://bugzilla.redhat.com/userprefs.cgi?tab=apikey
* Enter a name for the new key in the field under *New API Key*, e.g.
  'rhbztools', and click 'Submit Changes'.

Authentication information is stored in rhbugzilla/auth in your OS-specific
user config directory. On a typical Linux system this would be
*~/.config/rhbugzilla/auth*.

The contents of the file is a json formatted dict containing 2 keys:

* login: Your bugzilla login
* api_key: A valid API key for your login

e.g.

::

  {
      "login": "user@example.com",
      "api_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  }

bzdevelwb
=========

bzdevelwb is a tool for adding and removing keywords from a well-defined set to
the developer whiteboard of a number of bugzillas.

Keywords are defined in a keywords file. Each line of the file defines a
keyword. The first word on the line is the canonical representation of the
keyword, e.g. *ExampleKeyword*. Any subsequent words on the line are
alternative forms of the same keyword which will be automatically transformed
to the canonical version if encountered. Transformations are not case
sensitive, meaning *examplekeyword* will be rewritten as the canonical
*ExampleKeyword*.

Comments and blank lines are ignored in the keywords file.

E.g.:

::

  # Comments and blank lines are ignored

  NeedsAutomation NeedsAuto
  NeedsManualVer NeedsVer

In the above example, if *needsautomation*, *needsauto*, *NeedsAuto*, etc is
encountered in the devel whiteboard it will be automatically rewritten as
*NeedsAutomation*. Similarly, if any of the above are specified to be added or
removed from the devel whiteboard, any would be removed, or the canonical
version would be added.

bzdevelwb is invoked as:

::

  bzdevelwb [-h] [-a ADD [ADD ...]] [-r REMOVE [REMOVE ...]] -k KEYWORDS [-d]
            bzids [bzids ...]

e.g.:

::

  bzdevelwb -a needsauto -r needsver -k ~/compute-keywords.txt -- <bz1> <bz2> <bz3>

The above command will add NeedsAutomation to each of the 3 bugzillas, and
remove any variation of NeedsManualVer if encountered. Unknown keywords will be
left untouched.
