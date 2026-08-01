---
template: project
title: BudgetDeck Automation
description: A fully automated Excel VBA pipeline for department budget reporting — one click sorts, validates, collates, builds a PowerPoint deck, and emails it.
date: 2026-06-11
status: archived
tags: [vba, excel, automation]
github: https://github.com/yashtekavade/vba
live:
---

An end-to-end Excel-VBA automation pipeline: live dropdowns and validation on entry, a one-click "Run Full Refresh" that sorts and collates budget/actuals data, exports a PowerPoint deck straight from named ranges, and emails the finished deck via Outlook — all without leaving Excel.

**What it does**

- Department → Cost Center dropdowns auto-populate via `Worksheet_Change` events, with frozen rows auto-locked
- One-click pipeline: sort → validate (no blank mandatory fields) → collate into append-only sheets → export to PowerPoint → email via Outlook
- Cross-application automation (Excel → PowerPoint → Outlook) via late-bound Object Model calls
- Protected-sheet management (`UserInterfaceOnly:=True`) so VBA can write to locked sheets safely

**Why it's here**

Built as a portfolio demonstration of the VBA automation patterns used in real production reporting — event-driven UX, ETL-style validation gates, and cross-app orchestration — without any confidential data attached.
