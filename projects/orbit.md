---
template: project
title: Orbit
description: A prototype for a live, proximity-based social discovery app — see who's open to meet up nearby, right now.
date: 2026-07-27
status: wip
tags: [web, firebase, realtime]
github: https://github.com/yashtekavade/orbitt
live:
---

Orbit explores a simple idea: instead of matching with someone across the city, show who's actually nearby and open to meeting right now — at a campus, cafe, or event. Two modes are planned: Radar (1-on-1 discovery) and Hubs (place-based group chat).

**What's built so far**

- Anonymous auth with live location sync (geohash-based, coordinates fuzzed for privacy — exact GPS never leaves the device)
- Real-time 1-on-1 chat with a time-limited "approach" flow
- Ghost mode and a coarse "set my area" alternative to precise location sharing

**Status**

This is an active prototype, not a public app — core safety features (block, report, rate-limiting) aren't built yet, so it's intentionally not deployed or linked publicly until that groundwork is in place. Included here as a build-in-progress, not a finished product.
