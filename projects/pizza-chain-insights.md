---
template: project
title: Pizza Chain Insights
description: A cloud-native batch analytics pipeline for a multi-branch pizza chain — inventory, sales, and operational alerts on AWS.
date: 2025-08-08
status: archived
tags: [aws, python, etl]
github: https://github.com/yashtekavade/Pizza-Chain-Insights
live:
---

A batch analytics pipeline processing operational data (orders, inventory, discounts) across multiple pizza store locations, built to answer concrete business questions rather than just move data around.

**Architecture**

`Amazon RDS → AWS Glue → S3 → Athena`, with a parallel `Lambda → SQS → EC2 → SNS` path for threshold-based alerting (low inventory, discount anomalies).

**Business questions it answers**

- Top-selling SKUs per store over the last 7 days
- Category-wise revenue breakdown net of discounts
- Orders with discounts exceeding 30% of order value
- Low-inventory alerts based on weekend sales patterns
