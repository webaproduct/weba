# Changelog

## 17.0.0.22.0

### Bug Fixes
- Fixed issue in API controller where comments added through the API 
were not being sent to followers of the request. Refactored to use 
`message_post` method instead of direct message creation, ensuring 
proper notification delivery and improving consistency and security.
