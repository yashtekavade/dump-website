---
template: project
title: YouTube Comments ETL Pipeline
description: An end-to-end pipeline turning YouTube comment data into structured insight, orchestrated with Apache Airflow.
date: 2025-07-25
status: archived
tags: [airflow, python, etl]
github: https://github.com/yashtekavade/youtube_etl_airflow
live:
---

My first full end-to-end data pipeline project: pulling YouTube comments, running them through an ETL process, and orchestrating the whole thing with Airflow — treating a YouTube video's comment section as a real (if noisy) feedback data source.

**What it does**

- Extracts comment data via the YouTube API
- Transforms and cleans it into a structured format
- Loads it for downstream analysis, with Airflow managing the schedule and task dependencies
