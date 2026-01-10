# ADR-0001: Affordance-Driven REST with Mandatory Hypermedia Links

## Status
Accepted

## Context
This project demonstrates a RESTful API intended to support multiple clients
with differing levels of user-interface sophistication, without duplicating
business logic or hard-coding navigation rules in clients.

In many contemporary systems:
- Clients hard-code URL structures.
- Business rules leak into UI code.
- APIs devolve into "JSON over HTTP" without navigable structure.

This creates tight coupling, duplicated logic, and brittle systems.

## Decision
We adopt an **affordance-driven REST architecture** with the following rules:

1. **Hypermedia links are mandatory**
   - All responses include `_links` describing navigable resources.
   - Clients MUST navigate by following links.
   - Clients MUST NOT construct URLs by convention.

2. **Server authority**
   - The server is authoritative for permissions, workflow state, and allowed transitions.
   - Clients MUST NOT infer business rules from resource fields.

3. **Optional affordances**
   - `_actions` MAY describe executable capabilities available *now*.
   - `_forms` MAY describe input shapes for invoking actions.
   - `ui` hints MAY describe presentation-neutral interaction suggestions.
   - All optional affordances MUST be safe to ignore.

4. **No business logic in the UI**
   - UI code handles presentation and interaction only.
   - Business rules, validation, and state transitions reside exclusively on the server.

## Consequences

### Positive
- Multiple clients (CLI, web, mobile, kiosk) can consume the same API.
- Clients remain thin and resilient to server-side change.
- Navigation, permissions, and workflow remain correct even if optional metadata is ignored.
- APIs are self-describing and discoverable.

### Trade-offs
- Responses may be larger due to additional metadata.
- Clients must understand basic hypermedia concepts.
- Some implementation effort shifts from clients to the API.

## Demonstrated By
This repository includes three clients consuming the same API:

1. **Client 1**: Ignores all optional affordances and navigates using `_links` only.
2. **Client 2**: Uses `_actions` and `_forms` to invoke server-defined behaviour.
3. **Client 3**: Uses all affordances, including `ui` hints, to enhance UX.

All three clients remain correct and functional.

## Rationale
This decision restores the original intent of REST as a graph of interactions,
rather than a collection of hard-coded endpoints, while allowing progressive
enhancement for richer user experiences.

## Related
- [RFC 9110 (HTTP Semantics)](https://www.rfc-editor.org/rfc/rfc9110.html)
- Roy Fielding, ["Architectural Styles and the Design of Network-based Software Architectures"](https://roy.gbiv.com/pubs/dissertation/fielding_dissertation.pdf)
