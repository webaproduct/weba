# Changelog

## Version 1.13.3

- Default mail templates for events about **request team assigned** can now be configured separately on each **request classifier**.
- A separate **cron job** was added to handle these mails. 
- The **Notification Settings** tab in **Request Type** has been deprecated and removed.
This update allows users to fully customize properties all mentioned mails, including the subject, recipients, body etc.

## Version 1.6.0

- Changed the meaning of filter *Unassigned* on request:
  - Before this version, it showed requests that had no assigned
    users (*does not matter if request have assigned team or not*).
  - After this change, it will show requests, that
    do not have assigned user **and** do not have assigned team.
- Added new filters:
  - *No user assigned* - Show all requests that are not assigned to user
  - *No team assigned* - Show all requests that are not assigned to team

## Version 1.2.0

- Added ability to manage team assignment notifications from request type

