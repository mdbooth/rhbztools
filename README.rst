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

bzquery
=======

bzquery is a tool for querying bugzilla using human-readable but arbitrarily
complex queries like:

::

  cf_internal_whiteboard substring "DFG:Compute" and
  bug_status in ["NEW", "ASSIGNED"] and not (
    keywords substring "Documentation" or
    component = "documentation"
  ) and flags contains "rhos-17.0+"

It returns results as a JSON list. By default it returns add fields, but
returned fields can be specified explicitly with the -f flag. It is invoked as:

::

  bzquery [-h] [-f FIELD] [-d] [-q QUERYFILE] query

By default, the output JSON will contain all fields of the returned bugs.
Specifying one or more fields with the `-f` option will restrict that output to
only those fields. The `id` field will always be included, whether specified or
not. In additional to all available bugzilla fields, a `bzurl` field may be
specified which will include the bugzilla URL of each bug.

Syntax
------

A basic expression takes the form:

::

  field operation value

Different operations require different value types. Value types are:

* Integers: 0
* Floating point: 0.1
* Strings: "this is a string"
* Lists: [0, "foo"]

Expressions can be joined with ``and`` (alternatively ``&``), and ``or``
(alternatively ``|``). ``and`` has higher precedence than ``or``. Expressions
can also be grouped in parentheses, which has the highest precedence. e.g.:

::

  component = "openstack-nova" & (
      bug_status = "NEW" or
      assigned_to = "mbooth@redhat.com")

Expressions and parenthesis groups can be negated by prefixing them with
``not`` (alternatively ``!``). e.g.:

::

  component = "openstack-nova" & not (
      bug_status = "NEW" or
      ! assigned_to = "mbooth@redhat.com")

Query file
----------

Queries can be read either by specifying them on the command line, or from a
query file. If a query file is used, bzquery will attempt to read queries from
a YAML formatted file, e.g.:

::

  osp17: >
      classification = "Red Hat" &
      product = "Red Hat OpenStack" &
      cf_internal_whiteboard contains "DFG:Compute" &
      not (
        keywords contains "Documentation" |
        component = "documentation"
      ) &
      flags contains "rhos-17.0+"
  
  osp16: >
      classification = "Red Hat" &
      product = "Red Hat OpenStack" &
      cf_internal_whiteboard contains "DFG:Compute" &
      not (
        keywords contains "Documentation" |
        component = "documentation"
      ) &
      flags contains "rhos-16.0+"

When specifing a query file, the `query` parameter is expected to be the name
of one of the queries in the query file, e.g.:

::

  bzquery -f queries.yaml -f summary osp17

If the given query name is not found it will instead be interpreted as a full query.

Fields
---------------

Available field names are:

======================================================= =====================================
percentage_complete                                     %Complete
alias                                                   Alias
component_a                                             Approved Component List
cf_approved_release                                     Approved Release
assigned_to                                             Assignee
assigned_to_realname                                    Assignee Real Name
attachments.submitter                                   Attachment creator
attach_data.thedata                                     Attachment data
attachments.description                                 Attachment description
attachments.filename                                    Attachment filename
attachments.isobsolete                                  Attachment is obsolete
attachments.ispatch                                     Attachment is patch
attachments.isprivate                                   Attachment is private
attachments.mimetype                                    Attachment mime type
blocked                                                 Blocks
bug_id                                                  Bug ID
cf_build_id                                             Build ID
component_c                                             Capacity Component List
cf_category                                             Category
cc                                                      CC
cclist_accessible                                       CC list accessible
delta_ts                                                Changed
classification                                          Classification
cf_clone_of                                             Clone Of
cf_epm_cdp                                              Close Duplicate Candidate
cf_cloudforms_team                                      Cloudforms Team
longdesc                                                Comment
longdescs.isprivate                                     Comment is private
comment_tag                                             Comment Tag
commenter                                               Commenter
cf_compliance_control_group                             Compliance Control Group
cf_compliance_level                                     Compliance Level
component                                               Component
content                                                 Content
creation_ts                                             Creation date
cf_crm                                                  CRM
cf_deadline                                             Current Deadline
cf_deadline_type                                        Current Deadline Type
cf_cust_facing                                          Customer Escalation
days_elapsed                                            Days since bug changed
deadline                                                Deadline
dependent_products                                      Dependent Products
dependson                                               Depends On
cf_conditional_nak                                      Devel Conditional NAK
cf_devel_whiteboard, or devel_whiteboard                Devel Whiteboard
cf_release_notes                                        Doc Text
cf_doc_type                                             Doc Type
docs_contact                                            Docs Contact
docs_contact_realname                                   Docs Contact Real Name
cf_docs_score                                           Docs Score
cf_documentation_action                                 Documentation
cf_environment                                          Environment
cf_epm_pri                                              EPM Priority
everconfirmed                                           Ever confirmed
extra_components                                        Extra Components
extra_versions                                          Extra Versions
cf_fixed_in, or fixed_in                                Fixed In Version
requestees.login_name                                   Flag Requestee
setters.login_name                                      Flag Setter
flagtypes.name, flags                                   Flags
bug_group                                               Group
rep_platform                                            Hardware
cf_srtnotes                                             Internal SRT notes
cf_internal_target_milestone                            Internal Target Milestone
cf_internal_target_release                              Internal Target Release
cf_internal_whiteboard, or internal_whiteboard          Internal Whiteboard
keywords                                                Keywords
cf_last_closed                                          Last Closed
last_visit_ts                                           Last Visit
ext_bz_bug_map.ext_bz_bug_id                            Link ID
ext_bz_bug_map.ext_status                               Link Status
external_bugzilla.description                           Link System Description
external_bugzilla.url                                   Link System URL
cf_mount_type                                           Mount Type
longdescs.count                                         Number of Comments
cf_epm_phd                                              Onsite Hardware Date
estimated_time                                          Orig. Est.
op_sys                                                  OS
cf_ovirt_team                                           oVirt Team
cf_partner                                              Partner
cf_epm_prf_state                                        Partner Requirement State
tag                                                     Personal Tags
cf_pgm_internal                                         PgM Internal
cf_pm_score, or pm_score                                PM Score
remaining_time                                          Points Left
work_time                                               Points Worked
agile_pool.name                                         Pool
bug_agile_pool.pool_id                                  Pool ID
bug_agile_pool.pool_order                               Pool Order
priority                                                Priority
product                                                 Product
cf_epm_ptl                                              Public Target Launch Date
qa_contact                                              QA Contact
qa_contact_realname                                     QA Contact Real Name
cf_qa_whiteboard, or qa_whiteboard                      QA Whiteboard
cf_qe_conditional_nak                                   QE Conditional NAK
cf_regression_status                                    Regression
reporter                                                Reporter
reporter_accessible                                     Reporter accessible
reporter_realname                                       Reporter Real Name
resolution                                              Resolution
cf_atomic                                               RHEL 7.3 requirements from Atomic Host
rh_rule                                                 Rule Engine Rule
see_also                                                See Also
bug_severity                                            Severity
bug_status, or status                                   Status
cf_story_points                                         Story Points
rh_sub_components                                       Sub Component
short_desc                                              Summary
target_milestone                                        Target Milestone
target_release                                          Target Release
cf_target_upstream_version                              Target Upstream Version
owner_idle_time                                         Time Since Assignee Touched
cf_type                                                 Type
cf_epm_put                                              Upstream Kernel Target
bug_file_loc                                            URL
cf_verified                                             Verified
cf_verified_branch                                      Verified Versions
version                                                 Version
view                                                    view
votes                                                   Votes
status_whiteboard                                       Whiteboard
cf_zstream_target_release, or zstream_target_release    ZStream Target Release
======================================================= =====================================

Query operations
-------------------------

Available operations are:

======================================  =====================================
equals, or =                            is equal to
notequals, or !=                        is not equal to
anyexact, in                            is equal to any of the strings
substring                               contains the string
casesubstring, or contains              contains the string (exact case)
notsubstring                            does not contain the string
anywordssubstr                          contains any of the strings
allwordssubstr                          contains all of the strings
nowordssubstr                           contains none of the strings
regexp, or ~                            matches regular expression
notregexp, or !~                        does not match regular expression
lessthan, or <                          is less than
lessthaneq, or <=                       is less than or equal to
greaterthan, or >                       is greater than
greaterthaneq, or >=                    is greater than or equal to
anywords                                contains any of the words
allwords                                contains all of the words
nowords                                 contains none of the words
changedbefore                           changed before
changedafter                            changed after
changedfrom                             changed from
changedto                               changed to
changedby                               changed by
matches                                 matches
notmatches                              does not match
isempty                                 is empty
isnotempty                              is not empty
listofbugs                              In the list of bugs
======================================  =====================================
