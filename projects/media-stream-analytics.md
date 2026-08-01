---
template: project
title: Media Stream Analytics
description: A real-time media streaming analytics platform — Kinesis, Glue, EMR Spark, Airflow, and Snowflake wired into one pipeline.
date: 2025-08-01
status: archived
tags: [aws, airflow, python]
github: https://github.com/yashtekavade/Media-Stream-Analytics
live:
---

An end-to-end pipeline for processing media viewership data in real time, combining several AWS services with Airflow orchestration and a Snowflake warehouse on the receiving end.

**Architecture**

Viewership events stream through **Kinesis**, trigger a **Lambda** function, get transformed by **AWS Glue**, processed at scale with **EMR Spark**, land in **Snowflake**, with the whole workflow orchestrated by **Apache Airflow** DAGs.

**Why it's here**

A good example of gluing together streaming ingestion, distributed processing, and warehousing into one coherent, orchestrated pipeline rather than treating each piece in isolation.
